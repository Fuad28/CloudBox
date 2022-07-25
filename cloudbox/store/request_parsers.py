from flask_restful import reqparse

import werkzeug

folder_asset_args= reqparse.RequestParser()
folder_asset_args.add_argument("name", type=str, help="name of the folder is required", required=True)

file_asset_args= reqparse.RequestParser()
file_asset_args.add_argument("file", type=werkzeug.datastructures.FileStorage, location=['files', 'form'])






#  {
#         "id": "62dd287e97bdd6809240fc6c",
#         "user_id": "2469ade9-84b4-4e1e-b3bc-6febb5d5d2da",
#         "is_folder": "False",
#         "parent": null,
#         "name": "new file 2",
#         "uri": "127.0.0.1/5000/api/v1/file/62dd287e97bdd6809240fc6c",
#         "size": null,
#         "created_at": "2022-07-24 12:09:50.831000",
#         "updated_at": "2022-07-24 12:09:50.831000",
#         "file_type": "xlsx",
#         "storage_link": null
#     }

# login_args= reqparse.RequestParser()
# login_args.add_argument("email", type=email, help="email name of the user is required", required=True)
# login_args.add_argument("password", type=str, help="password is required", required=True)

