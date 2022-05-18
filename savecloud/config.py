import os
class Config:
    MONGODB_HOST = os.environ.get('SAVECLOUD_DATABASE_URI')
    SECRET_KEY= os.environ.get('FLASK_SECRET_KEY')