import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    #dbs
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
    S3_BUCKET_BASE_URL = os.environ.get("S3_BUCKET_BASE_URL")
    

    