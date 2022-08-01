from flask_restful import marshal
from flask import jsonify

from cloudbox import jwt_manager
from cloudbox.models import BaseAsset, User
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


def add_user_to_asset_access_list(asset: BaseAsset, access_type: str, req_users: list):
    """util function to perform addition of users to an asset's editors or viewers list"""

    #check that those editors truly exist
    user_emails= User.query.with_entities(User.email).filter(User.email.in_(req_users)).all()
    user_emails= [x[0] for x in user_emails]

    #get only emails that aren't already in the asset's editors or viewers list
    if access_type== "editors":
        new_user_emails= [x for x in user_emails if x not in asset.editors]
        asset.editors.extend(new_user_emails)
    else:
        new_user_emails= [x for x in user_emails if x not in asset.viewers]
        asset.viewers.extend(new_user_emails)

    asset.save()
    return asset

def remove_user_from_asset_access_list(asset: BaseAsset, access_type: str, req_users: list):
    """util function to perform removal of users from an asset's editors or viewers list"""

    if access_type=='editor':
        for x in req_users:
            if x in asset.editors:
                asset.editors.remove(x)

    else:
        for x in req_users:
            if x in asset.viewers:
                asset.viewers.remove(x)

    asset.save()
    return asset