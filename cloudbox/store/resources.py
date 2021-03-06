# from flask import abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource,  marshal_with
from sqlalchemy.orm import load_only

import os

from cloudbox import nosql_db
from cloudbox.http_status_codes import *
from cloudbox.models import FolderAsset, FileAsset, BaseAsset, User

from ..services.upload import upload_file_to_s3
from ..services.upload_utils import process_file_to_stream

from .fields import folder_asset_fields, file_asset_fields, asset_editors_fields, asset_viewers_fields
from .utils import combined_folder_file_response, single_entity_response
from .request_parsers import folder_asset_args, file_asset_update_args, file_asset_creation_args, asset_editors_viewers_args
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
    @marshal_with(file_asset_fields)
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

            if user_has_storage_space(user_id, asset_size):
                asset= FileAsset(
                    user_id= user_id, 
                    is_folder= False, 
                    parent= parent, 
                    name= file.filename.split('.')[0],
                    file_type= file.filename.split('.')[1],
                    size= asset_size)
                asset.save()

                #upload asset to aws
                data= process_file_to_stream(args["file"], to_utf8= True)
                upload_file_to_s3.delay(data, asset.id)
                # asset= FileAsset.objects.get(id= "62e2fa102804d8d90ed5596a")

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
        1. Can???t add viewers/editors to root folders
        2. Owner can add editors and viewers
        3. Editors can perform 1
        4. Owners and editors can see all other collaborators
        5. If general access level is set to editor, then users get editors privileges and can perform 1, 2 &3
        6. Viewers can see owners and themselves
        7. Non editors can only see owner (if the asset is unrestricted)

    """
    @marshal_with(asset_editors_fields)
    @jwt_required(optional= True)
    def get(self, id= None):
        #both verified and anonymous users can access this endpoint
        user_id= get_jwt_identity()

        if id is None:
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        elif user_id is None:
            asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "id": id})

            if asset.anyone_can_access == "editor":
                return asset, HTTP_200_OK
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_401_UNAUTHORIZED

        else:
            #user is logged in and an id was provided
            asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "id": id})

            if restricted_to_owner_editors_general_editors_CUD(asset, user_id):
                return asset, HTTP_200_OK
            
            else:
                return NOT_ALLOWED_TO_VIEW_ERROR, HTTP_403_FORBIDDEN

    @marshal_with(asset_editors_fields)
    @jwt_required()
    def post(self, id= None):
        args= asset_editors_viewers_args.parse_args(strict=True)
        user_id= get_jwt_identity()

        if id is None:
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND

        asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "id": id})
        
        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):
            #check that those editors truly exist
            editors_emails= User.query.filter(User.email.in_(args.editors)).options(load_only(User.email)).all()

            new_editors_emails= [x for x in editors_emails if x not in asset.editors]
            asset.editors.extend(new_editors_emails)
            asset.save()

            #send mail: args.notify  >>>

            return asset, HTTP_201_CREATED

        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN
    
  
    @jwt_required()
    def delete(self, id= None):
        user_id= get_jwt_identity()
        args= asset_editors_viewers_args.parse_args(strict=True)

        if id is None:
            return INVALID_ID_ERROR, HTTP_404_NOT_FOUND
        
        asset= BaseAsset.objects.get_or_404(__raw__= {"parent": {"$exists": True}, "id": id})

        if restricted_to_owner_editors_general_editors_CUD(asset, user_id):
            asset.editors= [x for x in asset.editors if x not in args.editors]  
            asset.save()
            return {}, HTTP_204_NO_CONTENT
        return NOT_ALLOWED_TO_PERFORM_ACTION_ERROR, HTTP_403_FORBIDDEN


class AssetViewers(Resource):
    pass