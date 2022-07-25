from flask import Blueprint
from flask_restful import Api
from .resources import Register, Login, Profile, TokenRefresh, RequestResetPassword, ResetPassword

auth= Blueprint('auth', __name__, url_prefix='/api/v1/auth/')
auth_api= Api(auth)


auth_api.add_resource(Register, "/register")
auth_api.add_resource(Login, "/login")
auth_api.add_resource(Profile, "/profile")
auth_api.add_resource(TokenRefresh, "/token/refresh")
auth_api.add_resource(RequestResetPassword, "/request-password-reset")
auth_api.add_resource(ResetPassword, "/reset-password")