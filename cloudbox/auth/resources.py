from flask import request, render_template, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from flask_restful import Resource,  marshal_with 

from werkzeug.security import check_password_hash, generate_password_hash
import os
import datetime
import base64
from io import BytesIO

from cloudbox import sql_db
from cloudbox.http_status_codes import *
from cloudbox.models import User

from ..mailer import send_email
from .utils import upload_profile_picture

from .fields import register_fields, login_fields, profile_fields, token_ref_fields
from .request_parsers import register_args,  login_args, forgot_password_args, reset_password_args
from .signals import user_registered

class Register(Resource):
    @marshal_with(register_fields)
    def post(self):
        args= register_args.parse_args(strict=True)

        password_hash= generate_password_hash(args['password'])
        args.pop('password', None)

        USER_ADDED_PROFILE_PICTURE= False
        if args.get('profile_pict') is not None:
            USER_ADDED_PROFILE_PICTURE= True
            encoded_img= base64.b64encode(args["profile_pict"].read())
            image_bytes= BytesIO(base64.b64decode(encoded_img))
            
        #set the profile picture to the default pending the time image is uploaded or even if profile picture wasn't sent
        args['profile_pict']= os.getenv("DEFAULT_PROFILE_PICTURE")

        user= User(password=password_hash, **args) 
        sql_db.session.add(user)
        sql_db.session.commit()

        # send signal
        user_registered.send(current_app._get_current_object(), user= user)
    
        #upload profile picture to cloudinary if any
        if USER_ADDED_PROFILE_PICTURE:
            print("Sendingggg??")
            upload_profile_picture.delay(image_bytes= image_bytes, user_id= user.id)


        return user, HTTP_201_CREATED

class Login(Resource):
    @marshal_with(login_fields)
    def post(self):
        args= login_args.parse_args(strict=True)
        email= args.get("email", None)
        password= args.get("password", None)

        user= User.query.filter_by(email=email).first()

        if user:
            check_pass= check_password_hash(user.password, password)

            if check_pass:
                refresh= create_refresh_token(identity= user.id)
                access= create_access_token(identity= user.id, expires_delta= datetime.timedelta(hours=24))
                
                return {'refresh': refresh, 'access': access}, HTTP_200_OK

        return {'error': 'Wrong credentials'}, HTTP_401_UNAUTHORIZED


class Profile(Resource):
    @marshal_with(profile_fields)
    @jwt_required()
    def get(self):
        user_id= get_jwt_identity()
        user= User.query.get(user_id)
        
        return user, HTTP_200_OK


class TokenRefresh(Resource):
    @marshal_with(token_ref_fields)
    @jwt_required(refresh= True)
    def get(self):
        user_id= get_jwt_identity()
        access= create_access_token(identity= user_id)

        return {"access": access}, HTTP_200_OK


class RequestResetPassword(Resource):
    def post(self):
        args= forgot_password_args.parse_args(strict=True)

        user = User.query.filter_by(email=args['email']).first()
        if not user:
            return {'error': 'Wrong credentials'}, HTTP_401_UNAUTHORIZED

        expires = datetime.timedelta(hours=24)
        reset_token = create_access_token(str(user.id), expires_delta=expires)

        # url = Api.url_for(self, endpoint= 'auth.reset', token=reset_token, _external=True)
  
        url= f"{request.host_url}reset-password/{reset_token}"
        #send password request reset  mail
        send_email.delay(
            subject= 'Reset Your Password',
            recipients=[user.email],
            text_body=render_template('email/reset_password.txt', url= url),
            html_body=render_template('email/reset_password.html', url= url))
        
        return {"message": "A mail has been sent to reset your password "}, HTTP_200_OK

class ResetPassword(Resource):
    @jwt_required()
    def post(self):
        args= reset_password_args.parse_args(strict=True)
        user_id= get_jwt_identity()
        user = User.query.get(user_id)

        password_hash= generate_password_hash(args['password'])
        user.password = password_hash
        sql_db.session.commit()

        #send success mail
        send_email.delay(
            subject= 'Password reset successful',
            recipients=[user.email],
            text_body='Password reset was successful',
            html_body='<p>Password reset was successful</p>')

        return {"message": "Password  reset successful"}, HTTP_200_OK