from flask import Flask, render_template, Blueprint, request
from flask_login import current_user, login_required

main= Blueprint('main', __name__)

# @main.route("/")
# @main.route("/home")
# def home():
#     if not current_user.is_authenticated:
#         return render_template('main/index.html')
#     return render_template('main/index_auth.html')