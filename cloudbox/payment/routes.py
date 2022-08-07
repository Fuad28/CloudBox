from flask import Blueprint
from flask_restful import Api
from .resources import Payment

payment= Blueprint('payment', __name__, url_prefix='/api/v1/payment/')
payment_api= Api(payment)


payment_api.add_resource(Payment, "/", "/verify/<string:reference_id>")