from flask import request, render_template, current_app, abort, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from flask_restful import Resource,  marshal_with, marshal



from cloudbox import nosql_db
from cloudbox.http_status_codes import *
from cloudbox.models import User, FolderAsset, FileAsset, BaseAsset

from ..services.upload import upload_profile_picture

from .fields import folder_asset_fields, file_asset_fields
from .utils import combined_folder_file_response, single_entity_response
from .request_parsers import folder_asset_args, file_asset_args

            
class Folder(Resource):
    @jwt_required(optional= True)
    def get(self, id= None):
        #both verified and anonymous users can access this endpoint
        user_id= get_jwt_identity()

        if (id is None) & (user_id is None):
            #user isn't logged in and no valid id is provided
            return {"error": "Enter a valid ID"}, HTTP_404_NOT_FOUND

        elif id is None:
            #user is logged in but an id isn't provided, return the user's root folder
            asset= BaseAsset.objects(user_id= user_id, parent= None).first()
            return single_entity_response(asset)

        else:
            #user is logged in and an id was provided, load the requested folder's children
            assets=  BaseAsset.objects(parent= id).all()
            return combined_folder_file_response(assets), HTTP_200_OK

    @marshal_with(folder_asset_fields)
    @jwt_required()
    def post(self, id= None):
        #only verified owners of assets and those in the asset's editors' list can access
        args= folder_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        #no id means a user is creating a folder in  their root folder
        parent= BaseAsset.objects(user_id= user_id, parent= None).first() if id is None else \
            BaseAsset.objects.get_or_404(id=id)

        editors_list= parent.editors

        if (user_id == parent.user_id) | (user_id in editors_list): 
            #user is owner or an editor of parent folder in which the new folder is being created
            asset= FolderAsset(user_id= user_id, is_folder= True, parent= parent, name= args.get('name'))
            asset.save()
            return single_entity_response(asset), HTTP_201_CREATED
        return abort(403), HTTP_403_FORBIDDEN

    @jwt_required()
    def patch(self, id= None):
        args= folder_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        if id is None:
            #means we're updating the name of the root folder 
            asset= BaseAsset.objects(user_id= user_id, parent= None).first()
        else:
            asset= BaseAsset.objects(parent= id).first()
        
        # if user_id in asset.editors:
        asset.update(name= args.get('name'))
        asset.save()
        return single_entity_response(asset), HTTP_200_OK
        
            

    @jwt_required()
    def delete(self, id= None):
        args= folder_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        if id is None:
            #means we're deleting the root folder which is impossible
            return abort(401), HTTP_403_FORBIDDEN
        else:
            asset= BaseAsset.objects(id= id).first()
            if user_id == asset.user_id: #bascially check it's in the editors list 
                asset.delete()
                return "", HTTP_204_NO_CONTENT
            else:
                return abort(403), HTTP_403_FORBIDDEN
        

class File(Resource):
    pass