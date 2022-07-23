import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image
import os

from cloudbox import sql_db
from cloudbox.models import User
from cloudbox import celery

#set up cloudinary
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)


def save_picture(media):
    """reduce profile picture sizes"""
    output_size = (125, 125)
    return Image.open(media).thumbnail(output_size)


@celery.task
def upload_profile_picture(media, user_id):
    """Upload media to cloudinary"""

    cloud_url= cloudinary.uploader.upload(media, folder= "profile")
    user= User.query.get(user_id)
    user.profile_pict= cloud_url.get("url")
    sql_db.session.commit()
    return cloud_url


    