from flask_restful import reqparse

import werkzeug

folder_asset_args= reqparse.RequestParser()
folder_asset_args.add_argument("name", type=str, help="name of the folder is required", required=True)

file_asset_creation_args= reqparse.RequestParser()
file_asset_creation_args.add_argument("file", type=werkzeug.datastructures.FileStorage, location=['files', 'form'])

file_asset_update_args= reqparse.RequestParser()
file_asset_update_args.add_argument("name", type=str, required=True)

asset_editors_viewers_args= reqparse.RequestParser()
asset_editors_viewers_args.add_argument("users", type=str, help="users list is required", required=True, action= 'append')
asset_editors_viewers_args.add_argument("notify", type=bool, required=True)

asset_editors_viewers_removal_args= reqparse.RequestParser()
asset_editors_viewers_removal_args.add_argument("users", type=str, help="users list is required", required=True, action= 'append')