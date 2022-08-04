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
import math

from ..models import BaseAsset, FileAsset, User
from .utils import send_storage_space_warning_email

def _user_is_logged_in(user_id: str):
    """used in permissions where user log in is necessary"""
    if user_id is None:
        return False

def if_no_ID_404(id: str):
    """First chheck for endpoints that require ID"""
    if id is None:
        return {"error": "Enter a valid ID"}, 400

def get_email(user_id: str):
    return User.query.get_or_404(user_id).email

        

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
            | (get_email(user_id) in asset.editors) \
                | (get_email(user_id) in asset.viewers):

        return True

    return False


def restricted_to_owner_editors_general_editors_CUD(asset: BaseAsset, user_id: str= None):
    """
    1. User must be logged in
    2. User is either owner or general access isnt restricted or user belongs to the asset's 
        #viewers or editors list
    """
    _user_is_logged_in(user_id)

    if (user_id== asset.user_id) | (asset.anyone_can_access == 'editor') | (get_email(user_id) in asset.editors):
        return True
    return False


def user_has_storage_space(user_id: str, asset_size: int):
    """Check if a user has storage space for asset being uploaded"""
    user= User.query.get(user_id)
    user_max_storage= user.max_storage_size()
    user_used_storage= FileAsset.objects.filter(user_id= user_id).sum('size')
    space_used= math.floor(user_used_storage/user_max_storage) * 100

    if (space_used > 75):
        #send mail if user has used up to 805 of their storage space
        send_storage_space_warning_email([user.mail], space_used)

    if (user_max_storage - user_used_storage) > asset_size:
        return True
    return False