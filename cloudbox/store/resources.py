# from flask import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource,  marshal_with

import os

from cloudbox import nosql_db
from cloudbox.http_status_codes import *
from cloudbox.models import FolderAsset, FileAsset, BaseAsset

from ..services.upload import upload_file_to_s3
from ..services.upload_utils import process_file_to_stream

from .fields import folder_asset_fields, file_asset_fields
from .utils import combined_folder_file_response, single_entity_response
from .request_parsers import folder_asset_args, file_asset_args
from .permissions import (unrestricted_R, restricted_to_owner_viewers_editors_general_R,
restricted_to_owner_viewers_editors_general_CUD, user_has_storage_space)

            
class FolderContent(Resource):
    @jwt_required(optional= True)
    def get(self, id= None):
        """both verified and anonymous users can access this endpoint"""

        user_id= get_jwt_identity()

        if (id is None) & (user_id is None):
            #user isn't logged in and no valid id is provided
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        elif id is None:
            #user is logged in but an id isn't provided, return content of the user's root folder
            user_root= FolderAsset.objects.get_or_404(user_id= user_id, parent= None)
            assets= BaseAsset.objects.filter(parent= user_root)
            return combined_folder_file_response(assets)

        elif user_id is None:
            #an id is provided but user is not logged in
            parent= FolderAsset.objects.get_or_404(id= id)
            assets= BaseAsset.objects.filter(parent= parent)

            if unrestricted_R(parent, user_id):
                return combined_folder_file_response(assets), HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            parent= FolderAsset.objects.get_or_404(id= id)

            if restricted_to_owner_viewers_editors_general_R(parent, user_id):
                assets=  BaseAsset.objects.filter(parent= parent)
                return combined_folder_file_response(assets), HTTP_200_OK
            
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_403_FORBIDDEN

class Folder(Resource):
    @jwt_required(optional= True)
    def get(self, id= None):
        #both verified and anonymous users can access this endpoint
        user_id= get_jwt_identity()

        if (id is None) & (user_id is None):
            #user isn't logged in and no valid id is provided
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        elif id is None:
            #user is logged in but an id isn't provided, return content of the user's root folder
            user_root= FolderAsset.objects.get_or_404(user_id= user_id, parent= None)
            return single_entity_response(user_root)

        elif user_id is None:
            #an id is provided but user is not logged in
            asset= FolderAsset.objects.get_or_404(id= id)

            if unrestricted_R(asset, user_id):
                return single_entity_response(asset), HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            asset= FolderAsset.objects.get_or_404(id= id)

            if restricted_to_owner_viewers_editors_general_R(asset, user_id):
                return single_entity_response(asset), HTTP_200_OK
            
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_403_FORBIDDEN

    @marshal_with(folder_asset_fields)
    @jwt_required()
    def post(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is parent asset id
        args= folder_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        #no id means a user is creating a folder in  their root folder
        parent= FolderAsset.objects(user_id= user_id, parent= None).first() if id is None else \
            FolderAsset.objects.get_or_404(id=id)

        if restricted_to_owner_viewers_editors_general_CUD(parent, user_id): 
            asset= FolderAsset(user_id= user_id, is_folder= True, parent= parent, name= args.get('name'))
            asset.save()
            return single_entity_response(asset), HTTP_201_CREATED
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN

    @jwt_required()
    def patch(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being updated id

        args= folder_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        #id None means we're updating the name of the root folder 
        asset= FolderAsset.objects.get_or_404(user_id= user_id, parent= None) if id is None else \
            FolderAsset.objects.get_or_404(id= id)

        if restricted_to_owner_viewers_editors_general_CUD(asset, user_id):      
            #perform the update if: the user owns the asset, is in the asset's editors list or 
            # the asset's anyone_can_access is editor
            asset.update(name= args.get('name'))
            asset.save()
            return single_entity_response(asset), HTTP_200_OK
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN
        
  
    @jwt_required()
    def delete(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being deleted id and it can't be none

        if id is None:
            return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN

        user_id= get_jwt_identity()
        asset= FolderAsset.objects.get_or_404(id= id)

        if restricted_to_owner_viewers_editors_general_CUD(asset, user_id):      
            #perform the delete if: the user owns the asset, is in the asset's editors list or 
            # the asset's anyone_can_access is editor
            asset.delete()
            return {"msg": "asset deleted"}, HTTP_204_NO_CONTENT
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN

class File(Resource):
    @jwt_required(optional= True)
    def get(self, id= None):
        #both verified and anonymous users can access this endpoint
        user_id= get_jwt_identity()

        if id is None:
            #if an id isn't provided
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        elif user_id is None:
            #an id is provided but user is not logged in
            asset= FileAsset.objects.get_or_404(id= id)

            if unrestricted_R(asset, user_id):
                return single_entity_response(asset), HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            asset= FileAsset.objects.get_or_404(id= id)

            if restricted_to_owner_viewers_editors_general_R(asset, user_id):
                return single_entity_response(asset), HTTP_200_OK
            
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_403_FORBIDDEN

    @marshal_with(file_asset_fields)
    @jwt_required()
    def post(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is parent asset id
        args= file_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()


        #no id means a user is uploading a file in  their root folder
        parent= FolderAsset.objects.get_or_404(user_id= user_id, parent= None) if id is None else \
            FolderAsset.objects.get_or_404(id=id)

        if restricted_to_owner_viewers_editors_general_CUD(parent, user_id):
            #check if user has enough storage space for the comming asset
            asset_size = os.stat(args["file"]).st_size
            if user_has_storage_space(user_id, asset_size):
                asset= FileAsset(user_id= user_id, is_folder= True, parent= parent, name= args.get('name'), size= asset_size)
                asset.save()

                #upload asset to aws
                data= process_file_to_stream(args["file"])
                upload_file_to_s3(data, asset.id)

                return single_entity_response(asset), HTTP_201_CREATED
            else: 
                return NOT_ENOUGH_SPACE_ERROR, HTTP_403_FORBIDDEN

        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN

    @jwt_required()
    def patch(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being updated id

        args= file_asset_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        if id is None:
            #if an id isn't provided
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        asset= FileAsset.objects.get_or_404(id= id)

        if restricted_to_owner_viewers_editors_general_CUD(asset, user_id):      
            #perform the update if: the user owns the asset, is in the asset's editors list or 
            # the asset's anyone_can_access is editor
            asset.update(name= args.get('name'))
            asset.save()
            return single_entity_response(asset), HTTP_200_OK
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN
        
  
    @jwt_required()
    def delete(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being deleted id and it can't be none

        if id is None:
            #if an id isn't provided
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        user_id= get_jwt_identity()
        asset= FolderAsset.objects.get_or_404(id= id)

        if restricted_to_owner_viewers_editors_general_CUD(asset, user_id):      
            #perform the delete if: the user owns the asset, is in the asset's editors list or 
            # the asset's anyone_can_access is editor
            asset.delete()
            return ASSET_DELETED_SUCCESS, HTTP_204_NO_CONTENT
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN