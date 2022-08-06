from flask_restful import fields

folder_asset_fields= {
    'id': fields.String,
    "user_id": fields.String,
    "is_folder": fields.String,
    "parent": fields.String(attribute= 'parent.id'),
    "name": fields.String,
    "uri": fields.String,
    "size": fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
}