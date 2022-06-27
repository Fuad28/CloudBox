from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Api, Resource, reqparse, fields, marshal_with

import werkzeug
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from datetime import datetime

from cloudbox import sql_db
from cloudbox.http_status_codes import *
from cloudbox.models import User

auth= Blueprint('auth', __name__, url_prefix='/api/v1/auth/')
auth_api= Api(auth)

"""
add_resource can take multiple endpoints=> api.add_resource(HelloWorld, '/','/hello')

reqparse => incoming requests

args = parser.parse_args(strict=True) => Calling parse_args with strict=True ensures that an error is thrown if the request includes arguments your parser does not define.

marshall_wit and fields => more like serializers

utility func=>
def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


structure=> args => fields => Resource => add_resource (at the end)
"""


#register endpoint
register_args= reqparse.RequestParser()
#personal
register_args.add_argument("first_name", type=str, help="first name of the user is required", required=True)
register_args.add_argument("last_name", type=str, help="last name of the user is required", required=True)
register_args.add_argument("middle_name", type=str)
register_args.add_argument("email", type=validators.email, help="email name of the user is required", required=True)
register_args.add_argument("password", type=str, help="password is required", required=True)
register_args.add_argument("country", type=str)
register_args.add_argument("phone", type=str)
register_args.add_argument("date_of_birth", type=str)
register_args.add_argument("profile_pict", type=werkzeug.datastructures.FileStorage, location='files')
#security question
register_args.add_argument("security_quest", type=str)
register_args.add_argument("security_ans", type=str)
#recovery info
register_args.add_argument("recovery_mail", type=validators.email)
register_args.add_argument("recovery_no", type=str)


register_fields= {
    'id': fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "middle_name": fields.String,
    "email": fields.String,
    "phone": fields.String,
    "profile_pict": fields.String,
    "date_of_birth": fields.DateTime,
}
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


# @auth.post('/register')
# def register():
#     username= request.json["username"]
#     email= request.json["email"]
#     password= request.json["password"]

#     if len(password) < 6:
#         return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

#     if len(username) < 3:
#         return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

#     if not username.isalnum() or " " in username:
#         return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

#     if not validators.email(email):
#         return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

#     if User.query.filter_by(email=email).first() is not None:
#         return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

#     if User.query.filter_by(username=username).first() is not None:
#         return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT

#     password_hash= generate_password_hash(password)
#     user= User(username=username, password= password_hash, email=email) 
#     db.session.add(user)
#     db.session.commit()

#     return jsonify(
#         {
#         'message': "User created",
#         'user': {'username': username, "email": email}
#         }
#         ), HTTP_201_CREATED


@auth.post('/login')
def login():
    email= request.json.get("email", None)
    password= request.json.get("password", None)

    user= User.query.filter_by(email=email).first()

    if user:
        check_pass= check_password_hash(user.password, password)

        if check_pass:
            refresh= create_refresh_token(identity= user.id)
            access= create_access_token(identity= user.id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
                }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED

@auth.get('/me') 
@jwt_required()
def me():
    user_id= get_jwt_identity()
    user= User.query.get(user_id)

    return jsonify({
        "username": user.username,
        "email": user.email
    }), HTTP_200_OK

@auth.get('/token/refresh')
@jwt_required(refresh= True)
def refresh_users_token():
    user_id= get_jwt_identity()
    access= create_access_token(identity= user_id)

    return jsonify({"access": access}), HTTP_200_OK




auth_api.add_resource(Register, "/register")