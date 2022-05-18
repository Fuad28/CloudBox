import os
class Config:
    MONGODB_HOST = os.environ.get('SAVECLOUD_DATABASE_URI')
    print(MONGODB_HOST)
    SECRET_KEY= os.environ.get('FLASK_SECRET_KEY')