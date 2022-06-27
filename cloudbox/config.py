import os
class Config:
    #dbs
    MONGODB_HOST = os.environ.get('CLOUDBOX_NOSQL_DB_URI')
    SQLALCHEMY_DATABASE_URI=os.environ.get('CLOUDBOX_SQL_DB_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY= os.environ.get('FLASK_SECRET_KEY')
    JWT_SECRET_KEY="JWT_SECRET_KEY"
    
    # MAIL_SERVER = 'smtp.sendgrid.net'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'apikey'
    # MAIL_PASSWORD = os.environ.get('FLASK_API_KEY')
    # MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_HOST_SENDGRID')