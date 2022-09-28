from flask import render_template, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, marshal_with

from cloudbox.http_status_codes import *
from cloudbox import sql_db
from cloudbox.models import Transaction, User

from .fields import transaction_fields
from .utils import upgrade_user_subscription, verify_payment


class Payment(Resource):
    @jwt_required(optional=True)
    def get(self):
        headers = {"Content-Type": "text/html"}
        user_id = get_jwt_identity()

        if user_id is None:
            return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED

        user = User.query.get(user_id)
        # user= User.query.get("10533f60-ce79-457d-8075-268c5bfaa86d")

        return make_response(
            render_template(
                "payment/paystack_payment.html",
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
            ),
            200,
            headers,
        )


class PaymentVerification(Resource):
    @marshal_with(transaction_fields)
    def get(self, reference_id):
        """Handles the callback function"""
        transaction = Transaction.query.filter_by(reference_id=reference_id).all()

        if len(transaction) == 0:
            data = verify_payment(reference_id)

            transaction = Transaction(**data)
            sql_db.session.add(transaction)
            sql_db.session.commit()

            upgrade_user_subscription(data["user"].id, str(int(data["amount"])))

        else:
            if transaction[0].status != "success":
                data = verify_payment(reference_id)
                transaction[0].status = data["status"]
                sql_db.session.commit()

                if data["status"] == "success":
                    upgrade_user_subscription(data["user"].id, str(int(data["amount"])))

        return transaction, HTTP_200_OK

    def post(self):
        """Handles the webhhook"""
        print("hereee 1")
        data= request.get_json()
        print("hereee 2")
        print(data)

        if data["event"] == "charge.success":
            reference_id= data["data"]["reference"]
            return self.get(reference_id)
        
        return "", 400


class Payments(Resource):
    @marshal_with(transaction_fields)
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        transactions = Transaction.query.filter_by(user_id=user_id).all()

        return transactions