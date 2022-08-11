from flask import Blueprint
from flask_restful import Api
from .resources import Payment, PaymentVerification, Payments

payment= Blueprint('payment', __name__, url_prefix='/api/v1/payments/')
payment_api= Api(payment)


payment_api.add_resource(Payments,  "/")
payment_api.add_resource(Payment, "pay/")
payment_api.add_resource(PaymentVerification,  "/verify/<string:reference_id>", "/<string:reference_id>", "/verify/webhook/")