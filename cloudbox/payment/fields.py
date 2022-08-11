from flask_restful import fields

transaction_fields= {
    'id': fields.Integer,
    "user_id": fields.String,
    "reference_id": fields.String,
    "amount": fields.Integer,
    "status": fields.String,
    "created_at": fields.DateTime
}