from flask import Flask
from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mail_sendgrid import MailSendGrid
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

import os
import cloudinary

from .config import Config


nosql_db= MongoEngine()
sql_db= SQLAlchemy()
# mail= Mail()
mail= MailSendGrid()
bcrypt= Bcrypt()
migrate = Migrate()
jwt_manager= JWTManager()



def create_app(config_class= Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    JWTManager(app)
    nosql_db.init_app(app)
    sql_db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt_manager.init_app(app)
    migrate.init_app(app, sql_db)
    from cloudbox.core.routes import core
    from cloudbox.auth.routes import auth

    app.register_blueprint(core)
    app.register_blueprint(auth)

    return app

#set up cloudinary
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)