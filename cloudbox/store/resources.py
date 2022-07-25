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

        elif user_id is None:
            #an id is provided but user is not logged in
            asset= BaseAsset.objects(id= id).first()

            if (asset.anyone_can_access != 'restricted'):
                #if asset is not restricted
                return combined_folder_file_response(assets), HTTP_200_OK
            else:
                return {"error": "You're not allowed to view, request access"}, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            asset= BaseAsset.objects(id= id).first()

            if (user_id== asset.user_id) | (asset.anyone_can_access != 'restricted') | (user_id in asset.editors) | (user_id in asset.viewers):
                # if user is either owner or general access isnt restricted or user belongs to the asset's viewers or editors list, load asset's children
                assets=  BaseAsset.objects(parent= id).all()
                return combined_folder_file_response(assets), HTTP_200_OK
            
            else:
                return abort(403), HTTP_403_FORBIDDEN

    @marshal_with(folder_asset_fields)
    @jwt_required()
    def post(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is parent asset id
        args= folder_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        #no id means a user is creating a folder in  their root folder
        parent= BaseAsset.objects(user_id= user_id, parent= None).first() if id is None else BaseAsset.objects.get_or_404(id=id)

        if (user_id == parent.user_id) | (user_id in parent.editors) | (parent.anyone_can_access == "editor"): 
            #user is owner or an editor of parent folder or parent folder anyone_can_access is set to editor
            asset= FolderAsset(user_id= user_id, is_folder= True, parent= parent, name= args.get('name'))
            asset.save()
            return single_entity_response(asset), HTTP_201_CREATED
        return {"error": "You're not allowed to perform this actiom, request access"}, HTTP_403_FORBIDDEN

    @jwt_required()
    def patch(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being updated id

        args= folder_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        #id None means we're updating the name of the root folder 
        asset= BaseAsset.objects.get(user_id= user_id, parent= None) if id is None else BaseAsset.objects.get(id= id)

        
        if (user_id == asset.user_id) | (user_id in asset.editors) | (asset.anyone_can_access == "editor"):      
        #perform the update if: the user owns the asset, is in the asset's editors list or the asset's anyone_can_access is editor
            asset.update(name= args.get('name'))
            asset.save()
            return single_entity_response(asset), HTTP_200_OK
        return {"error": "You're not allowed to perform this actiom, request access"}, HTTP_403_FORBIDDEN
        
  

    @jwt_required()
    def delete(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being deleted id and it can't be none

        if id is None:
            return {"error": "You're not allowed to perform this actiom, request access"}, HTTP_403_FORBIDDEN

        user_id= get_jwt_identity()
        asset= BaseAsset.objects.get(id= id)

        if (user_id == asset.user_id) | (user_id in asset.editors) | (asset.anyone_can_access == "editor"):      
        #perform the delete if: the user owns the asset, is in the asset's editors list or the asset's anyone_can_access is editor
            asset.delete()
            return {"msg": "asset deleted"}, HTTP_204_NO_CONTENT
        return {"error": "You're not allowed to perform this actiom, request access"}, HTTP_403_FORBIDDEN
        

class File(Resource):
    pass