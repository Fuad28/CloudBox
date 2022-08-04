import os
import shutil
from io import BytesIO
from zipfile import ZipFile

from flask import Response, redirect

import cloudinary
import cloudinary.uploader
import cloudinary.api

from cloudpathlib import CloudPath

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

from cloudbox import sql_db
from cloudbox.models import User, FileAsset, FolderAsset
from cloudbox import celery
from .upload_utils import *

#configure cloudinary
cloudinary.config( 
	cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
	api_key = os.environ.get('CLOUDINARY_API_KEY'), 
	api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

#configure boto3
s3 = boto3.client(
	"s3", 
	aws_access_key_id= os.environ.get("AWS_ACCESS_KEY_ID"), 
	aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY"),
	config=Config(
		signature_version="s3v4",
		region_name= os.environ.get("AWS_CLOUDBOX_REGION", "eu-central-1")
		)
	)


@celery.task
def upload_profile_picture(image_bytes, user_id):
		"""Upload data: dict to cloudinary"""

		cloud_url= cloudinary.uploader.upload(image_bytes, folder= "profile")
		user= User.query.get(user_id)
		user.profile_pict= cloud_url.get("url")
		sql_db.session.commit()
		return cloud_url


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