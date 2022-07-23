from flask_restful import reqparse

folder_asset_args= reqparse.RequestParser()
folder_asset_args.add_argument("id", type=str, help="first name of the user is required", required=True, location='form')



# login_args= reqparse.RequestParser()
# login_args.add_argument("email", type=email, help="email name of the user is required", required=True)
# login_args.add_argument("password", type=str, help="password is required", required=True)

