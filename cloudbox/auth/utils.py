from flask_mail import Message
# from flask import current_app

import  validators
import cloudinary
from PIL import Image
from flask import url_for

from cloudbox import mail
from cloudbox.models import User


def send_reset_email(user):
    token= user.get_reset_token()
    msg= Message(
        "Password reset request", 
        recipients= [user.email])
    msg.body= f"""To reset your password, visit {url_for("reset_token", token=token, _external=True)}
If you did not make this request, simply ignore this enail"""
    mail.send(msg)


def email(email_str):
    """Return email_str if valid, raise an exception in other case."""
    if validators.email(email_str):
        return email_str
        
    elif len(User.query.filter(email= email_str)) > 0:
        raise ValueError(f'Email {email_str} exists already')
    else:
        raise ValueError(f'{email_str} is not a valid email')


def save_picture(form_picture):
    """reduce profile picture sizes"""
    output_size = (125, 125)
    return Image.open(form_picture).thumbnail(output_size)


def upload_media(media):
    """Upload media to cloudinary"""
    return cloudinary.uploader.upload(media)
