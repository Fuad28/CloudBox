from flask import Blueprint
from flask_restful import Api
from resources import Register, Login, Profile, TokenRefresh

auth= Blueprint('auth', __name__, url_prefix='/api/v1/auth/')
auth_api= Api(auth)


auth_api.add_resource(Register, "/register")
auth_api.add_resource(Login, "/login")
auth_api.add_resource(Profile, "/profile")
auth_api.add_resource(TokenRefresh, "/token/refresh")


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