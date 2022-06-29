import cloudinary
from PIL import Image

from cloudbox import sql_db
from cloudbox.models import User
from cloudbox import celery

def save_picture(media):
    """reduce profile picture sizes"""
    output_size = (125, 125)
    return Image.open(media).thumbnail(output_size)


@celery.task
def upload_profile_picture(media, user_id):
    """Upload media to cloudinary"""
    media= save_picture(media)
    cloud_url= cloudinary.uploader.upload(media)
    user= User.query.get(user_id)
    user.profile_pict= cloud_url
    sql_db.session.commit()
    print(cloud_url)

    return cloud_url


    