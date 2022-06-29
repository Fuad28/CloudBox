from cloudbox import sql_db, nosql_db

from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid


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
    profile_pict= sql_db.Column(sql_db.String(20), default= "default.jpg")
    #security question
    security_quest= sql_db.Column(sql_db.String(20))
    security_ans= sql_db.Column(sql_db.String(20))
    #recovery
    recovery_mail= sql_db.String(sql_db.String(120))
    recovery_no= sql_db.Column(sql_db.String(20))

    created_at = sql_db.Column(sql_db.DateTime, default=datetime.now())
    updated_at = sql_db.Column(sql_db.DateTime, onupdate=datetime.now(), default=datetime.now())


    def __repr__(self):
        return f"User('{self.first_name}',  '{self.id}')"


class BaseAsset(nosql_db.Document):
    user_id= nosql_db.StringField(binary= False, required=True)
    is_folder= nosql_db.BooleanField(required= True)
    parent= nosql_db.StringField(binary= False, required=True)
    name= nosql_db.StringField(max_length=255, required= True)
    created_at = nosql_db.DateTimeField(required=True, default=datetime.now)
    updated_at = nosql_db.DateTimeField(required=True, default=datetime.now)

    def save(self, force_insert=False, validate=True, clean=True, write_concern=None, cascade=None, cascade_kwargs=None,_refs=None, save_condition=None, signal_kwargs=None, **kwargs):
        self.updated_at = datetime.datetime.now()
        super().save(force_insert, validate, clean, write_concern, cascade, cascade_kwargs, _refs, save_condition,signal_kwargs, **kwargs)

    meta = {'allow_inheritance': True}

class FileAsset(BaseAsset):
    file_type= nosql_db.StringField(required= True)
    storage_link= nosql_db.URLField(required= False)

    def get_uri(self):
        return f"{self.domain}/file/{self._id}"

    def get_size(self):
        pass

    def __repr__(self):
        return f"File('{self.name}')"

class FolderAsset(BaseAsset):
    def get_uri(self):
        return f"{self.domain}/folder/{self._id}"

    def __repr__(self):
        return f"Folder('{self.name}')"













#  def get_reset_token(self):
#         s= serializer(current_app.config["FLASK_SECRET_KEY"])
#         return s.dumps({"user_id": self.id})

#     @staticmethod
#     def verify_reset_token(token, expires_sec= 1800):
#         s= serializer(current_app.config["FLASK_SECRET_KEY"])
#         try:
#             user_id= s.loads(token, expires_sec)["user_id"]
#         except:
#             return None
#         return User.objects.get(user_id)

