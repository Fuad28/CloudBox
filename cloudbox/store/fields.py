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

file_asset_fields= folder_asset_fields | {
    "file_type": fields.String,
    "s3_key": fields.String
    }
    
asset_editors_fields= {
    'id': fields.String,
    'editors': fields.String
    }

asset_viewers_fields= {
    'id': fields.String,
    'viewers': fields.String
    }

asset_general_access_fields= {
    'id': fields.String,
    'anyone_can_access': fields.String(attribute= "anyone_can_access.name")}