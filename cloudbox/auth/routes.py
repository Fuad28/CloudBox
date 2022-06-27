from flask import Flask, render_template, Blueprint, request, redirect, url_for, current_app, flash, session, abort

from .utils import save_picture, send_reset_email
from cloudbox import sql_db, bcrypt
from cloudbox.models import User

auth= Blueprint('auth', __name__, url_prefix='/api/v1/auth/')


# @auth.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if current_user.is_authenticated:
#         print(current_user.first_name)
#         return redirect(url_for('main.home'))

#     form= RegistrationForm()

#     if form.validate_on_submit():
#         print("validate")
#         hashed_pw= bcrypt.generate_password_hash(form.password.data).decode("utf8")

#         user= User(
#             first_name= form.first_name.data,
#             last_name= form.last_name.data,
#             middle_name= form.middle_name.data,
#             email= form.email.data,
#             password= hashed_pw,
#             phone= form.phone.data,
#             date_of_birth= form.date_of_birth.data,
#             profile_pict= form.profile_pict.data,
#             security_quest= form.security_quest.data,
#             security_ans= form.security_ans.data,
#             recovery_mail= form.recovery_mail.data,
#             recovery_no= form.recovery_no.data,
#             )

#         if form.profile_pict.data:
#             user.profile_pict= save_picture(form.profile_pict.data)
        
#         if form.country.data:
#             user.country= save_picture(form.country.data)
#         user.save()

#         flash(f"Your account has been created! You're now able to login", "success")
#         return  redirect(url_for("auth.signin"))

#     return render_template('auth/auth-sign-up.html', title= "Register", form=form)


# @auth.route("/signin", methods= ["POST", "GET"]) 
# def signin():

#     if current_user.is_authenticated:
#         return redirect(url_for("main.home"))
    
#     form= LoginForm()

#     if form.validate_on_submit():
#         user= User.objects.filter(email= form.email.data).first()

#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user, remember= form.remember.data)
#             next_page= request.args.get('next')
#             return redirect(url_for(next_page[1:])) if next_page else redirect(url_for("main.home"))
#         else:
#             flash(f"Login unsuccessful! Check email and password", "danger")


#     return render_template('auth/auth-sign-in.html', title= "Login", form=form)


# @auth.route('/signout')
# def signout():
#     logout_user()
#     return  redirect(url_for("main.home"))