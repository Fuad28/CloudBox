from flask import jsonify, render_template, Response, redirect
from flask_restful import marshal

import os
import shutil
from io import BytesIO
from zipfile import ZipFile

from mongoengine import connect, disconnect
from cloudpathlib import CloudPath
from botocore.exceptions import ClientError

from cloudbox import jwt_manager, celery
from cloudbox.config import s3
from cloudbox.models import BaseAsset, User, FolderAsset, FileAsset
from .fields import folder_asset_fields, file_asset_fields
from ..mailer import send_email


def combined_folder_file_response(qs):
    response= []
    for item in qs:
        if item.is_folder:
            response.append(marshal(item, folder_asset_fields) | {"uri": item.get_uri()})
        else:
            response.append(marshal(item, file_asset_fields) | {"uri": item.get_uri()})
    return response


def single_entity_response(entity):
    if entity.is_folder:
        return marshal(entity, folder_asset_fields) | {"uri": entity.get_uri()}
    else:
        return marshal(entity, file_asset_fields) | {"uri": entity.get_uri()}


# customise errror message
@jwt_manager.unauthorized_loader
def unauthorized_loader_callback(arg_1):
    return jsonify({"msg": "Missing credentials"})


def add_user_to_asset_access_list(asset: BaseAsset, access_type: str, req_users: list, notify: bool):
    """util function to perform addition of users to an asset's editors or viewers list"""

    #check that those editors truly exist
    user_emails= User.query.with_entities(User.email).filter(User.email.in_(req_users)).all()
    user_emails= [x[0] for x in user_emails]

    #get only emails that aren't already in the asset's editors or viewers list
    if access_type== "editors":
        new_user_emails= [x for x in user_emails if x not in asset.editors]
        asset.editors.extend(new_user_emails)
    else:
        new_user_emails= [x for x in user_emails if x not in asset.viewers]
        asset.viewers.extend(new_user_emails)

    if notify & len(new_user_emails):
        #send notification to user
        send_access_notification_email(req_users, asset, access_type)

    asset.save()
    return asset

def remove_user_from_asset_access_list(asset: BaseAsset, access_type: str, req_users: list):
    """util function to perform removal of users from an asset's editors or viewers list"""

    if access_type=='editor':
        for x in req_users:
            if x in asset.editors:
                asset.editors.remove(x)

    else:
        for x in req_users:
            if x in asset.viewers:
                asset.viewers.remove(x)

    asset.save()
    return asset

def send_access_notification_email(users_mails: list, asset: BaseAsset, access_type: str):
    """Send email notification to users that thhey  have been added as an asset's viewer or editor"""
    send_email.delay(
        subject= f'Notification of access to asset {asset.name}',
        recipients= users_mails,
        text_body=render_template(
            'email/access_notification.txt',
            asset_name= asset.name,
            asset_url= asset.get_uri(),
            access_type= access_type.title()
            ),

        html_body=render_template(
            'email/access_notification.html',
            asset_name= asset.name,
            asset_url= asset.get_uri(),
            access_type= access_type.title()
            )
        )

def send_storage_space_warning_email(user_mail: list, space_used):
    """Alert users of using up 80% storage space"""
    send_email.delay(
        subject= f'Storage almost full',
        recipients= user_mail,
        text_body=render_template('email/storage_notification.txt', space_used= space_used),
        html_body=render_template('email/storage_notification.html', space_used= space_used)
        )
def _unique_filename(filename, parent_folder_files):
    if filename in parent_folder_files:
        return False
    return True


def unique_secure_filename(filename, parent_folder_files):
    """Returns secure and unique filename"""
    filename= filename.split(".")[0]
    for i in range(1, 1000):
        if not _unique_filename(filename, parent_folder_files):
            filename= f"{filename[:-3].strip()} ({i})" if i >1 else f"{filename} ({i})"
            continue
        return filename
        

def mongo_connect():
    """
    We are supposed to connect to the  database inside the task.
    The reason is because child processes (created by Celery) must have their own instance of mongo client.
    re: https://stackoverflow.com/questions/49743258/mongodb-into-a-celery-task-flask-application

    """
    disconnect(alias='default')
    return connect(host= os.getenv("CLOUDBOX_NOSQL_DB_URI"))


@celery.task
def upload_file_to_s3(file_path: str, asset_id: str) -> str:
		"""
		Upload file to S3
		"""
		#create mongodb connection
		mongo_connect()
		asset= FileAsset.objects.get(id= asset_id)

		s3.upload_file(
			file_path,
			os.environ.get("S3_BUCKET_NAME"),
			f"{asset.s3_key}",
			ExtraArgs={"ContentType": asset.file_type}
			)
		
		#delete file
		os.remove(file_path)


def view_file(asset: FileAsset) -> str:
		"""
		view file from S3 bucket
		"""
		
		response= s3.generate_presigned_url(
			'get_object',
			Params= {'Bucket': os.environ.get("S3_BUCKET_NAME"), 'Key': asset.s3_key},
			ExpiresIn=3600
			)

		return redirect(response, code= 302)


def download_file_asset(asset: FileAsset) -> str: 
	""" download file from S3 bucket """
	try:
		file = s3.get_object(Bucket=os.environ.get("S3_BUCKET_NAME"), Key=asset.s3_key)
		return Response(
				file['Body'].read(),
				mimetype= asset.file_type,
				headers={"Content-Disposition": f"attachment;filename={asset.name}.{asset.file_type.split('/')[1]}"}
				)
		
	except ClientError as e:
		if e.response['Error']['Code'] == "404":
				print("The object does not exist.")
		else:
			return e

def get_all_file_paths(directory: str):
	file_paths = []

	# crawling through directory and subdirectories
	for root, directories, files in os.walk(directory):
		for filename in files:
			# join the two strings in order to form the full filepath.
			filepath = os.path.join(root, filename)
			file_paths.append(filepath)

	return file_paths		

def convert_file_to_zip(directory: str):
	"""directory: path to folder which needs to be zipped"""

	file_paths = get_all_file_paths(directory)
	s = BytesIO() #to store the zipped file as bytes
	
	# writing files to a zipfile
	with ZipFile(s,'w') as zip: #ZipFile(f'{zipped_file_name}.zip','w')
		# writing each file one by one
		for file in file_paths:
			filename= file.removeprefix(directory)
			zip.writestr(filename, file)

	return s


def download_folder_asset(asset: FolderAsset):
	"""Downloads folder assets to local download directory"""


	s3_folder= asset.s3_key.split('/')[-1]
	local_dir= os.path.expanduser(f'~/Downloads/{s3_folder}')
	s3_folder= asset.s3_key

	try:
		cp = CloudPath(f"s3://{os.getenv('S3_BUCKET_NAME')}/{s3_folder}")
		cp.download_to(local_dir)
		# return jsonify({"Success": f'{local_dir}'})
		s= convert_file_to_zip(local_dir)
		
		#remove the downloaded one from server
		shutil.rmtree(local_dir)

		return Response(
				s.getvalue(),
				mimetype= "application/x-zip-compressed",
				content_type="application/x-zip-compressed",
				headers={"Content-Disposition": f"attachment;filename={asset.name}.zip"}
				)


	except ClientError as e:
		if e.response['Error']['Code'] == "404":
				print("The object does not exist.")
		else:
			return e