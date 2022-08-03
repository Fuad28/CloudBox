import os

from flask import Response, redirect, jsonify

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
      f"{asset.s3_key}",
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


def download_folder_asset(asset: FolderAsset):
  """Downloads folder assets to local download directory"""

  s3_folder= asset.s3_key.split('/')[-1]
  local_dir= os.path.expanduser(f'~/Downloads/{s3_folder}')
  s3_folder= asset.s3_key

  try:
    cp = CloudPath(f"s3://{os.getenv('S3_BUCKET_NAME')}/{s3_folder}")
    cp.download_to(local_dir)
    return jsonify({"Success": f'{local_dir}'})

  except ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
      return e