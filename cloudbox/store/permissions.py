"""
types of permissions

GET
1.unrestricted asset- anyone on internet with the link can view
2. restricted asset- only those listed below can view:
    a. owner
    b. editors and viewers

POST PATCH DELETE
1.unrestricted - any logged in user can perform actions
2. restricted asset- only those listed below can perform actions:
    a. owner
    b. editors

"""
from ..models import BaseAsset, FileAsset, User

def _user_is_logged_in(user_id: str):
    """used in permissions where user log in is necessary"""
    if user_id is None:
        return False
        

def unrestricted_R(asset: BaseAsset, user_id: str= None) -> bool:
    """ unrestricted GET"""

    if (asset.anyone_can_access != 'restricted'):
        return True
    return False

def restricted_to_owner_viewers_editors_general_R(asset: BaseAsset, user_id: str= None):
    """
    1. User must be logged in
    2. User is either owner or general access isnt restricted or user belongs to the asset's 
        #viewers or editors list
    3. GET
    """
    _user_is_logged_in(user_id)

    if (user_id== asset.user_id) \
        | (asset.anyone_can_access != 'restricted') \
            | (user_id in asset.editors) \
                | (user_id in asset.viewers):

        return True

    return False


def restricted_to_owner_viewers_editors_general_CUD(asset: BaseAsset, user_id: str= None):
    """
    1. User must be logged in
    2. User is either owner or general access isnt restricted or user belongs to the asset's 
        #viewers or editors list
    """
    _user_is_logged_in(user_id)

    if (user_id== asset.user_id) | (asset.anyone_can_access == 'editor') | (user_id in asset.editors):
        return True
    return False


def user_has_storage_space(user_id: str, asset_size: int):
    """Check if a user has storage space for asset being uploaded"""
    user_max_storage= User.query.get(user_id).max_storage_size
    user_used_storage= FileAsset.objects.filter(user_id= user_id).only('size').sum('size')

    print(asset_size)
    print(user_max_storage)
    print(user_used_storage)

    if (user_max_storage - user_used_storage) > asset_size:
        return True
    return False