from flask import jsonify, render_template
from flask_restful import marshal

from cloudbox import jwt_manager
from cloudbox.models import BaseAsset, User
from .fields import folder_asset_fields, file_asset_fields
from ..services.mailer import send_email


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


# customise errror message
@jwt_manager.unauthorized_loader
def unauthorized_loader_callback(arg_1):
    return jsonify({"msg": "Missing credentials"})


def add_user_to_asset_access_list(asset: BaseAsset, access_type: str, req_users: list, notify: bool):
    """util function to perform addition of users to an asset's editors or viewers list"""

    #check that those editors truly exist
    user_emails= User.query.with_entities(User.email).filter(User.email.in_(req_users)).all()
    user_emails= [x[0] for x in user_emails]

    #get only emails that aren't already in the asset's editors or viewers list
    if access_type== "editors":
        new_user_emails= [x for x in user_emails if x not in asset.editors]
        asset.editors.extend(new_user_emails)
    else:
        new_user_emails= [x for x in user_emails if x not in asset.viewers]
        asset.viewers.extend(new_user_emails)

    if notify & len(new_user_emails):
        #send notification to user
        send_access_notification_email(req_users, asset, access_type)

    asset.save()
    return asset

def remove_user_from_asset_access_list(asset: BaseAsset, access_type: str, req_users: list):
    """util function to perform removal of users from an asset's editors or viewers list"""

    if access_type=='editor':
        for x in req_users:
            if x in asset.editors:
                asset.editors.remove(x)

    else:
        for x in req_users:
            if x in asset.viewers:
                asset.viewers.remove(x)

    asset.save()
    return asset

def send_access_notification_email(users_mails: list, asset: BaseAsset, access_type: str):
    """Send email notification to users that thhey  have been added as an asset's viewer or editor"""
    send_email.delay(
        subject= f'Notification of access to asset {asset.name}',
        recipients= users_mails,
        text_body=render_template(
            'email/access_notification.txt',
            asset_name= asset.name,
            asset_url= asset.get_uri(),
            access_type= access_type.title()
            ),

        html_body=render_template(
            'email/access_notification.html',
            asset_name= asset.name,
            asset_url= asset.get_uri(),
            access_type= access_type.title()
            )
        )

def send_storage_space_warning_email(user_mail: list, space_used):
    """Alert users of using up 80% storage space"""
    send_email.delay(
        subject= f'Storage almost full',
        recipients= user_mail,
        text_body=render_template('email/storage_notification.txt', space_used= space_used),
        html_body=render_template('email/storage_notification.html', space_used= space_used)
        )
def _unique_filename(filename, parent_folder_files):
    if filename in parent_folder_files:
        return False
    return True


def unique_secure_filename(filename, parent_folder_files):
    """Returns secure and unique filename"""
    filename= filename.split(".")[0]
    for i in range(1, 1000):
        if not _unique_filename(filename, parent_folder_files):
            filename= f"{filename[:-3].strip()} ({i})" if i >1 else f"{filename} ({i})"
            continue
        return filename
        

