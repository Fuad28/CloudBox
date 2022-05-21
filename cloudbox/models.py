from cloudbox import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as serializer
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Document, UserMixin):
    #personal
    first_name= db.StringField(max_length=20, required=True)
    last_name= db.StringField(max_length=20, required=True)
    middle_name= db.StringField(max_length=20)
    email= db.EmailField(max_length=50, unique=True,required=True)
    password= db.StringField(max_length=100, required=True)
    coutry= db.StringField(max_length=50)
    date_of_birth= db.DateField()
    profile_pict= db.StringField(max_length=255, default= "default.jpg")
    #security question
    security_quest= db.StringField(max_length=255)
    security_ans= db.StringField(max_length=20)
    #recovery
    recovery_mail= db.EmailField(max_length=50)
    recovery_no= db.StringField(max_length=14)

    
    def get_reset_token(self):
        s= serializer(current_app.config["FLASK_SECRET_KEY"])
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec= 1800):
        s= serializer(current_app.config["FLASK_SECRET_KEY"])
        try:
            user_id= s.loads(token, expires_sec)["user_id"]
        except:
            return None
        return User.objects.get(user_id)


    def __repr__(self):
        return f"User('{self.first_name}',  '{self.email}',  '{self.profile_pict}')"
