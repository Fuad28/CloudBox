from flask import Flask
from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from .config import Config


nosql_db= MongoEngine()
sql_db= SQLAlchemy()
mail= Mail()
bcrypt= Bcrypt()



def create_app(config_class= Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    nosql_db.init_app(app)
    sql_db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    mail.init_app(app)

    from cloudbox.core.routes import core
    from cloudbox.auth.routes import auth

    app.register_blueprint(core)
    app.register_blueprint(auth)

    return app