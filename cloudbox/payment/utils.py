
import os
import requests

from cloudbox import sql_db
from cloudbox.models import User

def upgrade_user_subscription(user_id: str, amount: str):
    amount_to_plan= {
        "2000": "basic",
        "5000": "standard",
        "100000": "premium"
    }

    plan= amount_to_plan[amount]
    user= User.query.get(user_id)
    user.subscription_plan= plan
    sql_db.session.commit()

def verify_payment(reference_id: str):
    paystack_verify_url= f"https://api.paystack.co/transaction/verify/{reference_id}"
    PAYSTACK_SECRET_KEY= os.environ.get("PAYSTACK_SECRET_KEY")
    headers= {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}

    res= requests.get(paystack_verify_url, headers= headers).json()

    data= {
         "reference_id": res["data"]["reference"],
         "status": res["data"]["status"],
         "amount": res["data"]["amount"]/100,
         "created_at": res["data"]["created_at"]
    }
    user= User.query.filter_by(email= res["data"]["customer"]["email"]).first()
    data["user"]= user
    return data

    

