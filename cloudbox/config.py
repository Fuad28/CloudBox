import os
# from flask import Flask
# from celery import Celery
import cloudinary
import boto3
from botocore.client import Config
from dotenv import load_dotenv
load_dotenv()


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

#configuration variables for the flask app
class Config:
    MONGODB_HOST = os.environ.get('CLOUDBOX_NOSQL_DB_URI')
    SQLALCHEMY_DATABASE_URI=os.environ.get('CLOUDBOX_SQL_DB_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY= os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY= os.environ.get('JWT_SECRET_KEY')
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'
    MAIL_SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_HOST_SENDGRID')
    CELERY_RESULT_BACKEND= os.environ.get('CELERY_RESULT_BACKEND')
    CELERY_BROKER_URL= os.environ.get('CELERY_BROKER_URL')
    CELERY_ACCEPT_CONTENT = ['pickle']
    CELERY_TASK_SERIALIZER = 'pickle'
    CELERY_RESULT_SERIALIZER = 'pickle'
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")


class ProductionConfig(Config):
    MONGODB_HOST = os.environ.get('CLOUDBOX_NOSQL_DB_URI') # prod db PROD_CLOUDBOX_NOSQL_DB_URI
    SQLALCHEMY_DATABASE_URI=os.environ.get('CLOUDBOX_SQL_DB_URI') # prod db PROD_CLOUDBOX_SQL_DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY= os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY= os.environ.get('JWT_SECRET_KEY')
    CELERY_RESULT_BACKEND= os.environ.get('CELERY_RESULT_BACKEND') #prod redis db PROD_CELERY_RESULT_BACKEND
    CELERY_BROKER_URL= os.environ.get('CELERY_BROKER_URL') #prod celery server PROD_CELERY_BROKER_URL
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")