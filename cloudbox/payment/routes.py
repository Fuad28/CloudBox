from flask import Blueprint
from flask_restful import Api
from .resources import Payment

payment= Blueprint('payment', __name__, url_prefix='/api/v1/payment/')
payment_api= Api(payment)


payment_api.add_resource(Payment, "/payment/")


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