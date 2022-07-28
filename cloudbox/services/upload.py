import os
from PIL import Image

import cloudinary
import cloudinary.uploader
import cloudinary.api

import boto3

from cloudbox import sql_db
from cloudbox.models import User, FileAsset
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
  )


@celery.task
def upload_profile_picture(image_bytes, user_id):
    """Upload data: dict to cloudinary"""

    cloud_url= cloudinary.uploader.upload(image_bytes, folder= "profile")
    user= User.query.get(user_id)
    user.profile_pict= cloud_url.get("url")
    sql_db.session.commit()
    return cloud_url

from mongoengine import disconnect, connect
from celery.signals import task_prerun

# @task_prerun.connect
# def on_task_init(*args, **kwargs):
#     disconnect(alias='default')
    # connect(db, host=host, port=port, maxPoolSize=400, minPoolSize=200, alias='default')

@celery.task
def upload_file_to_s3(data: dict, asset_id: str) -> str:
    """
    Upload file to S3
    """
    file, content_type= process_stream_to_file(data)
    
    s3.upload_fileobj(
      file,
      os.environ.get("S3_BUCKET_NAME"),
      file.filename,
      ExtraArgs={"ContentType": content_type}
      )

    #create mongodb connection
    mongo_connect()

    asset= FileAsset.objects.get(id= asset_id)
    asset.storage_link= f"{os.getenv('S3_BUCKET_BASE_URL')}/{data['filename']}"
    asset.save()