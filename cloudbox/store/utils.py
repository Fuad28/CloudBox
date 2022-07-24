from flask_restful import marshal

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