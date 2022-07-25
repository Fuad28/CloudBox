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
from ..models import BaseAsset

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