from flask import request, render_template, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from flask_restful import Resource,  marshal_with, marshal



from cloudbox import nosql_db
from cloudbox.http_status_codes import *
from cloudbox.models import User, FolderAsset, FileAsset, BaseAsset

from ..services.upload import upload_profile_picture

from .fields import folder_asset_fields, file_asset_fields
from .utils import combined_folder_file_response
# from .request_parsers import 

            
    

class Folder(Resource):
    @jwt_required()
    def get(self, id= None):
        user_id= get_jwt_identity()

        if id is None:
            user_root= BaseAsset.objects(user_id= user_id, parent= "root").all()
            return combined_folder_file_response(user_root), HTTP_200_OK

        else:
            folder_assets=  BaseAsset.objects(parent= id).all()
            return combined_folder_file_response(folder_assets), HTTP_200_OK

    @jwt_required()
    def post(self, id= None):
        pass

    @jwt_required()
    def put(self, id= None):
        pass

    @jwt_required()
    def delete(self, id= None):
        pass

class File(Resource):
    pass

# class Profile(Resource):
#     @marshal_with(profile_fields)
#     @jwt_required()
#     def get(self):
#         user_id= get_jwt_identity()
#         user= User.query.get(user_id)

#         return user, HTTP_200_OK


# class TokenRefresh(Resource):
#     @marshal_with(token_ref_fields)
#     @jwt_required(refresh= True)
#     def get(self):
#         user_id= get_jwt_identity()
#         access= create_access_token(identity= user_id)

#         return {"access": access}, HTTP_200_OK


# class RequestResetPassword(Resource):
#     def post(self):
#         args= forgot_password_args.parse_args(strict=True)

#         user = User.query.filter_by(email=args['email']).first()
#         if not user:
#             return {'error': 'Wrong credentials'}, HTTP_401_UNAUTHORIZED

#         expires = datetime.timedelta(hours=24)
#         reset_token = create_access_token(str(user.id), expires_delta=expires)

#         # url = Api.url_for(self, endpoint= 'auth.reset', token=reset_token, _external=True)
  
#         url= f"{request.host_url}reset-password/{reset_token}"
#         #send password request reset  mail
#         send_email.delay(
#             subject= 'Reset Your Password',
#             recipients=[user.email],
#             text_body=render_template('email/reset_password.txt', url= url),
#             html_body=render_template('email/reset_password.html', url= url))
        
#         return {"message": "A mail has been sent to reset your password "}, HTTP_200_OK

# class ResetPassword(Resource):
#     @jwt_required()
#     def post(self):
#         args= reset_password_args.parse_args(strict=True)
#         user_id= get_jwt_identity()
#         user = User.query.get(user_id)

#         password_hash= generate_password_hash(args['password'])
#         user.password = password_hash
#         sql_db.session.commit()

#         #send success mail
#         send_email.delay(
#             subject= 'Password reset successful',
#             recipients=[user.email],
#             text_body='Password reset was successful',
#             html_body='<p>Password reset was successful</p>')

#         return {"message": "Password  reset successful"}, HTTP_200_OK