from flask_restful import marshal
from flask import jsonify

from cloudbox import jwt_manager
from .fields import folder_asset_fields, file_asset_fields

def combined_folder_file_response(qs):
    response= []
    for item in qs:
        if item.is_folder:
            response.append(marshal(item, folder_asset_fields) | {"uri": item.get_uri()})
        else:
            response.append(marshal(item, file_asset_fields) | {"uri": item.get_uri()})
    return response


def single_entity_response(entity):
    if entity.is_folder:
        return marshal(entity, folder_asset_fields) | {"uri": entity.get_uri()}
    else:
        return marshal(entity, file_asset_fields) | {"uri": entity.get_uri()}


# customise errror message
@jwt_manager.unauthorized_loader
def unauthorized_loader_callback(arg_1):
    return jsonify({"msg": "Missing credentials"})
