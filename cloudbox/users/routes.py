from flask import Flask, render_template, Blueprint, request, redirect, url_for, current_app, flash
from flask_login import login_user, current_user, logout_user, login_required

from .forms import LoginForm, RegistrationForm
from .utils import save_picture, send_reset_email
from cloudbox import db, bcrypt
from cloudbox.models import User



users= Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form= RegistrationForm()

    if form.validate_on_submit():
        hashed_pw= bcrypt.generate_password_hash(form.password.data).decode("utf8")
        user= User(
            first_name= form.first_name.data,
            last_name= form.last_name.data,
            middle_name= form.middle_name.data,
            email= form.email.data,
            password= hashed_pw,
            country= form.country.data,
            date_of_birth= form.date_of_birth.data,
            profile_pict= form.profile_pict.data,
            security_quest= form.security_quest.data,
            security_ans= form.security_ans.data,
            recovery_mail= form.recovery_mail.data,
            recovery_no= form.recovery_no.data,
            )

        if form.profile_pict.data:
            user.profile_pict= save_picture(form.picture.data)
        user.save()

        flash(f"Your account has been created! You're now able to login", "success")
        return  redirect(url_for("users.login"))

    return render_template('users/auth-sign-up.html', title= "Register", form=form)
    
@users.route("/login/", methods= ["POST", "GET"]) 
def login():
    pass
    # if current_user.is_authenticated:
    #     return redirect(url_for("main/home"))
    

#     # form= LoginForm()

#     if form.validate_on_submit():
#         user= User.query.filter_by(email= form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user, remember= form.remember.data)
#             next_page= request.args.get('next')
#             return redirect(url_for(next_page[1:])) if next_page else redirect(url_for("main.home"))
#         else:
#             flash(f"Login unsuccessful! Check email and password", "danger")
    
#     return render_template('login.html', title= "Login", form=form)
