from flask import Flask, render_template, Blueprint, request
from flask_login import current_user, login_required

core= Blueprint('core', __name__, url_prefix='/api/v1/core/')

@core.route("/")
@core.route("/home")
def home():
    if not current_user.is_authenticated:
        return render_template('core/index.html')
    return render_template('core/index_auth.html')