from flask_restful import fields

register_fields= {
    'id': fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "middle_name": fields.String,
    "email": fields.String,
    "phone": fields.String,
    "profile_pict": fields.String,
    "date_of_birth": fields.DateTime,
}

login_fields= {
    "access": fields.String,
    "refresh": fields.String,
}


profile_fields= {
    'id': fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "middle_name": fields.String,
    "email": fields.String,
    "phone": fields.String,
    "profile_pict": fields.String,
    "date_of_birth": fields.DateTime,
    "security_quest": fields.String,
    "security_ans": fields.String,
    "recovery_mail": fields.String,
    "recovery_no": fields.String,
}

token_ref_fields= {
    "access": fields.String
}