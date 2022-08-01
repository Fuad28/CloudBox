# from flask import abort
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource,  marshal_with, marshal
from mongoengine.fields import ObjectId

import os
import base64
from io import BytesIO

from cloudbox import nosql_db
from cloudbox.http_status_codes import *
from cloudbox.models import FolderAsset, FileAsset, BaseAsset, User

from ..services.upload import upload_file_to_s3, download_file, view_file
from ..services.upload_utils import process_file_to_stream

from .fields import (folder_asset_fields, file_asset_fields, asset_viewers_fields, asset_editors_fields,
 asset_general_access_fields)
from .utils import combined_folder_file_response, single_entity_response, add_user_to_asset_access_list, remove_user_from_asset_access_list
from .request_parsers import (folder_asset_args, file_asset_update_args, file_asset_creation_args, 
asset_editors_viewers_args, asset_editors_viewers_removal_args, asset_general_access_args)
from .permissions import (unrestricted_R, restricted_to_owner_viewers_editors_general_R,
restricted_to_owner_editors_general_editors_CUD, if_no_ID_404, user_has_storage_space)

            
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
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            parent= FolderAsset.objects.get_or_404(id= id)

            if restricted_to_owner_viewers_editors_general_R(parent, user_id):
                assets=  BaseAsset.objects.filter(parent= parent)
                return combined_folder_file_response(assets), HTTP_200_OK
            
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_403_FORBIDDEN

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
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            asset= FolderAsset.objects.get_or_404(id= id)

            if restricted_to_owner_viewers_editors_general_R(asset, user_id):
                return single_entity_response(asset), HTTP_200_OK
            
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_403_FORBIDDEN

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

        if restricted_to_owner_editors_general_editors_CUD(parent, user_id): 
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

        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):      
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

        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):      
            #perform the delete if: the user owns the asset, is in the asset's editors list or 
            # the asset's anyone_can_access is editor
            asset.delete()
            return {"msg": "asset deleted"}, HTTP_204_NO_CONTENT
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN

class File(Resource):
    # @marshal_with(file_asset_fields)
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
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            asset= FileAsset.objects.get_or_404(id= id)

            if restricted_to_owner_viewers_editors_general_R(asset, user_id):
                return single_entity_response(asset), HTTP_200_OK
            
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_403_FORBIDDEN


    @marshal_with(file_asset_fields)
    @jwt_required()
    def post(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is parent asset id
        args= file_asset_creation_args.parse_args(strict=True)
        user_id= get_jwt_identity()


        #no id means a user is uploading a file in  their root folder
        parent= FolderAsset.objects.get_or_404(user_id= user_id, parent= None) if id is None else \
            FolderAsset.objects.get_or_404(id=id)

        if restricted_to_owner_editors_general_editors_CUD(parent, user_id):
            #check if user has enough storage space for the comming asset
            
            file = args['file']
            file.seek(0, os.SEEK_END)
            asset_size = file.tell()
            file.seek(0, 0)

            splitted_filename= file.filename.split(".")

            if user_has_storage_space(user_id, asset_size):
                asset= FileAsset(
                    user_id= user_id, 
                    is_folder= False, 
                    parent= parent, 
                    name=  ".".join(splitted_filename[0:-1]),
                    file_type= file.content_type,
                    size= asset_size)
                asset.save()

                # upload asset to aws
                data= process_file_to_stream(args["file"], to_utf8= True)
                upload_file_to_s3.delay(data, asset.id)
                
                return single_entity_response(asset), HTTP_201_CREATED

            else: 
                return NOT_ENOUGH_SPACE_ERROR, HTTP_403_FORBIDDEN

        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN

    @jwt_required()
    def patch(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being updated id

        args= file_asset_update_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        if id is None:
            #if an id isn't provided
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        asset= FileAsset.objects.get_or_404(id= id)

        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):      
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
        asset= FileAsset.objects.get_or_404(id= id)

        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):      
            #perform the delete if: the user owns the asset, is in the asset's editors list or 
            # the asset's anyone_can_access is editor
            asset.delete()
            return ASSET_DELETED_SUCCESS, HTTP_204_NO_CONTENT
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN


class AssetEditors(Resource):
    """
        Editors and Viewers CRUD
        1. Can’t add viewers/editors to root folders
        2. Owner can add editors and viewers
        3. Editors can perform 1
        4. Owners and editors can see all other collaborators
        5. If general access level is set to editor, then users get editors privileges and can perform 1, 2 &3
        6. Viewers can see owners and themselves
        7. Non editors can only see owner (if the asset is unrestricted)

    """
    access_type= "editors"

    @jwt_required(optional= True)
    def get(self, id= None):
        #both verified and anonymous users can access this endpoint
        user_id= get_jwt_identity()

        if_no_ID_404(id)

        if user_id is None:
            asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "_id": ObjectId(id)})
            
            if asset.anyone_can_access == "editor":
                return (marshal(asset, asset_editors_fields), HTTP_200_OK) if self.access_type == "editors" else (marshal(asset, asset_viewers_fields), HTTP_200_OK)
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "_id": ObjectId(id)})
         
            if restricted_to_owner_editors_general_editors_CUD(asset, user_id):
                return (marshal(asset, asset_editors_fields), HTTP_200_OK) if self.access_type == "editors" else (marshal(asset, asset_viewers_fields), HTTP_200_OK)
                
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_403_FORBIDDEN

    @jwt_required()
    def post(self, id= None):
        args= asset_editors_viewers_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        if_no_ID_404(id)

        asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "_id": ObjectId(id)})
        
        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):
            asset= add_user_to_asset_access_list(asset, self.access_type, args.users)
            
            #send mail: args.notify, args.users  >>>
            return (marshal(asset, asset_editors_fields), HTTP_201_CREATED) if self.access_type == "editors" else (marshal(asset, asset_viewers_fields), HTTP_201_CREATED)
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN
    
  
    @jwt_required()
    def delete(self, id= None):
        user_id= get_jwt_identity()
        args= asset_editors_viewers_removal_args.parse_args(strict=True)

        if_no_ID_404(id)
        
        asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "_id": ObjectId(id)})

        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):
            asset= remove_user_from_asset_access_list(asset, self.access_type, args.users)
            return {}, HTTP_204_NO_CONTENT
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN


class AssetViewers(AssetEditors):
    access_type= "viewers"

class GeneralAccess(Resource):
    @jwt_required()
    def patch(self, id= None):
        #access given to: verified owners of assets, those in the asset's editors' list, 
        # if the asset's anyone_can_acess is editors
        #id is asset being updated id

        args= asset_general_access_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        if_no_ID_404(id)

        asset= asset= FileAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "_id": ObjectId(id)})

        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):      
            asset.update(anyone_can_access= args.get('access_type'))
            asset.save()
            return marshal(asset, asset_general_access_fields), HTTP_200_OK
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN

class DownloadAsset(Resource):
    @jwt_required(optional= True)
    def get(self, id= None):
        user_id= get_jwt_identity()

        if_no_ID_404(id)

        asset= BaseAsset.objects.get_or_404(id= id)

        if user_id is None:
            if unrestricted_R(asset, user_id):
                return download_file(asset), HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED
        else:
            if restricted_to_owner_viewers_editors_general_R(asset, user_id):
                return download_file(asset), HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_403_FORBIDDEN


class ViewFileAsset(Resource):
    @jwt_required(optional= True)
    def get(self, id= None):
        user_id= get_jwt_identity()

        if_no_ID_404(id)

        asset= BaseAsset.objects.get_or_404(id= id)

        if user_id is None:
            if unrestricted_R(asset, user_id):
                return view_file(asset), HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_401_UNAUTHORIZED
        else:
            if restricted_to_owner_viewers_editors_general_R(asset, user_id):
                return view_file(asset), HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_ACCESS_ERROR, HTTP_403_FORBIDDEN