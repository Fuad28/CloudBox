from flask_restful import reqparse
from .utils import email
import werkzeug

register_args= reqparse.RequestParser()
#personal
register_args.add_argument("first_name", type=str, help="first name of the user is required", required=True, location='form')
register_args.add_argument("last_name", type=str, help="last name of the user is required", required=True, location='form')
register_args.add_argument("middle_name", type=str, location='form')
register_args.add_argument("email", type=email, help="email of the user is required", required=True, location='form')
register_args.add_argument("password", type=str, help="password is required", required=True, location='form')
register_args.add_argument("country", type=str, location='form')
register_args.add_argument("phone", type=str, location='form')
register_args.add_argument("date_of_birth", type=str, location='form')
register_args.add_argument("profile_pict", type=werkzeug.datastructures.FileStorage, location=['files', 'form'])
#security question
register_args.add_argument("security_quest", type=str, location='form')
register_args.add_argument("security_ans", type=str, location='form')
#recovery info
register_args.add_argument("recovery_mail", type=email, location='form')
register_args.add_argument("recovery_no", type=str, location='form')


login_args= reqparse.RequestParser()
login_args.add_argument("email", type=email, required=True)
login_args.add_argument("password", type=str, help="password is required", required=True)

forgot_password_args= reqparse.RequestParser()
forgot_password_args.add_argument("email", type=email, help="email name of the user is required", required=True)

reset_password_args= reqparse.RequestParser()
reset_password_args.add_argument("password", type=str, help="new password is required", required=True)


