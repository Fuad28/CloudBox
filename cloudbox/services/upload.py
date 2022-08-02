import os

from flask import Response, redirect

import cloudinary
import cloudinary.uploader
import cloudinary.api

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
def upload_file_to_s3(data: dict, asset_id: str) -> str:
    """
    Upload file to S3
    """
    #create mongodb connection
    mongo_connect()
    asset= FileAsset.objects.get(id= asset_id)

    file, content_type= process_stream_to_file(data)

    s3.upload_fileobj(
      file,
      os.environ.get("S3_BUCKET_NAME"),
      f"{asset.parent.name}/{file.filename}",
      ExtraArgs={"ContentType": content_type}
      )
    

    asset.s3_key= f"{asset.parent.name}/{file.filename}"
    asset.save()


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


def download_file(asset: FileAsset) -> str: 
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



def download_folder_asset(asset: FolderAsset):
    """
    Download the contents of a folder directory
    Args:
        bucket_name: the name of the s3 bucket
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """
    s3 = boto3.resource('s3')
    local_dir= "CloudBox download"
    s3_folder= asset.name

    bucket = s3.Bucket(os.environ.get("S3_BUCKET_NAME"))

    for obj in bucket.objects.filter(Prefix=s3_folder):
      target = os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
      
      if not os.path.exists(os.path.dirname(target)):
          os.makedirs(os.path.dirname(target))
      if obj.key[-1] == '/':
          continue

    # for filename in file_names:
    # s3_template_path = queryset.values('file')  
    # conn = boto.connect_s3('<aws access key>', '<aws secret key>')
    # bucket = conn.get_bucket('your_bucket')
    # s3_file_path = bucket.get_key(s3_template_path)
    # response_headers = {
    # 'response-content-type': 'application/force-download',
    # 'response-content-disposition':'attachment;filename="%s"'% filename
    # }
    # url = s3_file_path.generate_url(60, 'GET',
    #             response_headers=response_headers,
    #             force_http=True)

    # # download the file
    # file_response = requests.get(url)  

    # if file_response.status_code == 200:

    #     # create a copy of the file
    #     f1 = open(filename , 'wb')
    #     f1.write(file_response.content)
    #     f1.close()

    #     # write the file to the zip folder
    #     fdir, fname = os.path.split(filename)
    #     zip_path = os.path.join(zip_subdir, fname)
    #     zf.write(filename, zip_path)    

    # # close the zip folder and return
    # zf.close()
    # response = HttpResponse(byte_stream.getvalue(), content_type="application/x-zip-compressed")
    # response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    # return response      