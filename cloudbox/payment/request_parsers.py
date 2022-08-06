from flask_restful import reqparse

import werkzeug

folder_asset_args= reqparse.RequestParser()
folder_asset_args.add_argument("name", type=str, help="name of the folder is required", required=True)

file_asset_creation_args= reqparse.RequestParser()
file_asset_creation_args.add_argument("file", type=werkzeug.datastructures.FileStorage, location=['files', 'form'], required=True)
