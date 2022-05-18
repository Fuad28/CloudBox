from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

from .config import Config


db= MongoEngine()
# login_manager= LoginManager()
# login_manager.login_view= 'users.login'






def create_app(config_class= Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    # login_manager.init_app(app)

    from savecloud.main.routes import main

    app.register_blueprint(main)

    return app