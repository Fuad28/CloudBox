from flask import current_app, render_template, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource,  marshal_with, marshal

from cloudbox.http_status_codes import *
from cloudbox import sql_db
from cloudbox.models import Transaction, User

from .fields import transaction_fields

import os
import requests
        
  
class Payment(Resource):
    @jwt_required(optional= True)
    def get(self):
        headers = {'Content-Type': 'text/html'}
        user_id= get_jwt_identity()

        # if user_id is None:
        #     return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED

        # user= User.query.get(user_id)
        user= User.query.get("10533f60-ce79-457d-8075-268c5bfaa86d")

        return make_response(
            render_template(
            'payment/paystack_payment.html',
            first_name= user.first_name,
            last_name= user.last_name,
            email= user.email
            ),
            200,
            headers)

    
    @marshal_with(transaction_fields)
    def post(self, reference_id):
        paystack_verify_url= f"https://api.paystack.co/transaction/verify/{reference_id}"
        PAYSTACK_SECRET_KEY= os.environ.get("PAYSTACK_SECRET_KEY")
        headers= {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}

        res= requests.get(paystack_verify_url, headers= headers).json()
        email= res["data"]["customer"]["email"]
        reference_id= res["data"]["reference"]
        status= res["data"]["status"]
        amount= res["data"]["amount"]/100
        user= User.query.filter_by(email= email).first()

        #check if there'is a record for that transaction in the database alread
        transaction= Transaction.query.filter_by(reference_id= reference_id)

        if len(transaction) == 0:
            transaction= Transaction(user=user, reference_id= reference_id, status= status,amount= amount)

            sql_db.session.add(transaction)
            sql_db.session.commit()
            
        else:
            if (transaction.status != "success") & (status == "success"):
                transaction.status= status
                sql_db.session.commit()
                
        
        return transaction,  HTTP_200_OK



