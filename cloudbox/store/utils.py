from flask_restful import marshal

from .fields import folder_asset_fields, file_asset_fields

def combined_folder_file_response(qs):
    response= []
    for item in qs:
        if item.is_folder:
            response.append(marshal(item, folder_asset_fields))
        else:
            response.append(marshal(item, file_asset_fields))
    return response