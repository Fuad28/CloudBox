from flask import Flask, render_template, Blueprint, request
from flask_login import current_user, login_required

main= Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')