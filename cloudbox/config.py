import os
class Config:
    MONGODB_HOST = os.environ.get('CLOUDBOX_DATABASE_URI')
    SECRET_KEY= os.environ.get('FLASK_SECRET_KEY')