from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Resource,  marshal_with


from werkzeug.security import check_password_hash, generate_password_hash

from cloudbox import sql_db
from cloudbox.http_status_codes import *
from cloudbox.models import User

from .fields import register_fields, login_fields, profile_fields, token_ref_fields
from .request_parsers import register_args,  login_args

class Register(Resource):
    @marshal_with(register_fields)
    def post(self):
        args= register_args.parse_args(strict=True)
        password_hash= generate_password_hash(args['password'])
        args.pop('password', None)
        user= User(password=password_hash, **args) 
        sql_db.session.add(user)
        sql_db.session.commit()
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
                access= create_access_token(identity= user.id)
                
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
