from flask_restful import fields

folder_asset_fields= {
    'id': fields.String,
    "user_id": fields.String,
    "is_folder": fields.String,
    "parent": fields.String,
    "name": fields.String,
    "uri": fields.String,
    "size": fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
}

file_asset_fields= folder_asset_fields | {"file_type": fields.String, "storage_link": fields.String}
