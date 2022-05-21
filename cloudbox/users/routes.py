from flask import Flask, render_template, Blueprint, request, redirect, url_for, current_app
from flask_login import login_user, current_user, logout_user, login_required

from cloudbox.users.forms import LoginForm

users= Blueprint('users', __name__)

# @users.route("/signup/", methods= ["POST", "GET"])
# def signup():
#     # if current_user.is_authenticated:
#     #     return redirect(url_for('main/home'))
#     return render_template('users/auth-sign-up.html')

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('users/auth-sign-up.html')
    
# @users.route("/login/", methods= ["POST", "GET"]) 
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("main/home"))

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
