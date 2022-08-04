"""Blueprint specific helper functions. Global helper functions can be found in services"""

import  validators
from cloudbox import celery, sql_db
from cloudbox.config import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudbox.models import User



def email(email_str):
    """Return email_str if valid, raise an exception in other case."""
    if validators.email(email_str):
        return email_str
    
    elif email_str== "":
        raise ValueError("email of the user is required")

    elif len(User.query.filter(email= email_str)) > 0:
        raise ValueError(f'Email {email_str} exists already')

    else:
        raise ValueError(f'{email_str} is not a valid email')

@celery.task
def upload_profile_picture(image_bytes, user_id):
		"""Upload data: dict to cloudinary"""

		cloud_url= cloudinary.uploader.upload(image_bytes, folder= "profile")
		user= User.query.get(user_id)
		user.profile_pict= cloud_url.get("url")
		sql_db.session.commit()
		return cloud_url