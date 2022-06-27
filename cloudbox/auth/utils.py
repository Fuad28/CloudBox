import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from cloudbox import mail
from flask import current_app
import  validators

def  save_picture(form_picture):
    random_hex= secrets.token_hex(8)
    _, f_ext= os.path.splitext(form_picture.filename)
    picture_fn= random_hex+f_ext
    picture_path= os.path.join(current_app.root_path, "static/profile_pics", picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

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
    else:
        raise ValueError('{} is not a valid email'.format(email_str))

#media upload service