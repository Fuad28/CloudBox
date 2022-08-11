from cloudbox import sql_db, nosql_db

from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from dotenv import load_dotenv
import os
import uuid
import enum

load_dotenv()
class SubscriptionPlanEnum(enum.Enum):
    free = 'free'
    basic = 'basic'
    standard = 'standard'
    premium = 'premium'

class AnyoneCanAcessEnum(enum.Enum):
    restricted = 'restricted'
    viewer = 'viewer'
    editor = 'editor'

class User(sql_db.Model):
    #personal
    id = sql_db.Column(UUID(as_uuid=True), primary_key=True, default= uuid.uuid4)
    first_name= sql_db.Column(sql_db.String(20), nullable=False)
    last_name= sql_db.Column(sql_db.String(20), nullable=False)
    middle_name= sql_db.Column(sql_db.String(20))
    email= sql_db.Column(sql_db.String(120), unique=True,nullable=False)
    password= sql_db.Column(sql_db.String(120), nullable=False)
    country= sql_db.Column(sql_db.String(20))
    phone= sql_db.Column(sql_db.String(20))
    date_of_birth= sql_db.Column(sql_db.DateTime, default=datetime.now())
    profile_pict= sql_db.Column(sql_db.String(255), default= "default.jpg")
    #security question
    security_quest= sql_db.Column(sql_db.String(20))
    security_ans= sql_db.Column(sql_db.String(20))
    #recovery
    recovery_mail= sql_db.String(sql_db.String(120))
    recovery_no= sql_db.Column(sql_db.String(20))

    created_at = sql_db.Column(sql_db.DateTime, default=datetime.now())
    updated_at = sql_db.Column(sql_db.DateTime, onupdate=datetime.now(), default=datetime.now())

    subscription_plan= sql_db.Column(
        sql_db.Enum(SubscriptionPlanEnum), default=SubscriptionPlanEnum.free, nullable=False
        )
    transactions= sql_db.relationship("Transaction", backref="user")

    def max_storage_size(self):
        hundred_mb= 1024 * 1024 * 100 
        sizes= {
            "free": hundred_mb,
            "basic": hundred_mb * 10,
            "standard": hundred_mb * 50,
            "premium": hundred_mb * 100
            }

        return sizes[str(self.subscription_plan.name)]
        

    def __repr__(self):
        return f"User('{self.first_name}',  '{self.id}')"

class Transaction(sql_db.Model):
    id = sql_db.Column(sql_db.Integer, primary_key=True)
    user_id= sql_db.Column(UUID(as_uuid=True), sql_db.ForeignKey("user.id"))
    reference_id= sql_db.Column(sql_db.String(50), nullable=False)
    amount=  sql_db.Column(sql_db.Float, nullable=False)
    status= sql_db.Column(sql_db.String(20))
    created_at = sql_db.Column(sql_db.DateTime)
        
    def __repr__(self):
        return f"Transaction({self.reference_id})"


class BaseAsset(nosql_db.Document):
    user_id= nosql_db.StringField(binary= False, required=True)
    editors= nosql_db.ListField(nosql_db.StringField())
    viewers= nosql_db.ListField(nosql_db.StringField())
    anyone_can_access= nosql_db.EnumField(AnyoneCanAcessEnum, default=AnyoneCanAcessEnum.restricted)
    is_folder= nosql_db.BooleanField(required= True, default= False)
    parent= nosql_db.ReferenceField("BaseAsset", reverse_delete_rule= nosql_db.CASCADE)
    uri= nosql_db.StringField()
    name= nosql_db.StringField(max_length=255, required= True)
    s3_key= nosql_db.StringField(required= False)
    created_at = nosql_db.DateTimeField(required=True, default=datetime.now)
    updated_at = nosql_db.DateTimeField(required=True, default=datetime.now)
    # parent= nosql_db.StringField(binary= False, required=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)

    meta = {'allow_inheritance': True}

class FileAsset(BaseAsset):
    file_type= nosql_db.StringField(required= True)
    size= nosql_db.FloatField(required= False)

    def get_uri(self):
        return f"{os.getenv('DOMAIN')}/api/v1/files/{self.id}"

    def __repr__(self):
        return f"File('{self.name}')"


class FolderAsset(BaseAsset):
    is_folder= nosql_db.BooleanField(required= True, default= True)

    def get_uri(self):
        return f"{os.getenv('DOMAIN')}/api/v1/folders/{self.id}"

    def __repr__(self):
        return f"Folder('{self.name}')"






















 
    # def get_size(self):
    #     return "helllooo"

    # def to_dict(self):

    #     init_dict= self.to_mongo().to_dict()

    #     # print(init_dict["_cls"].split("."))

    #     init_dict["uri"]= self.get_uri()
    #     init_dict["id"]= str(self.id)
    #     init_dict["created_at"]= str(self.created_at)
    #     init_dict["updated_at"]= str(self.updated_at)
    #     init_dict["size"]= self.get_size()
    #     init_dict.pop("_id")
    #     init_dict.pop("_cls")

    #     return init_dict




