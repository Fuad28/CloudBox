from flask import Flask
from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
from flask_mail_sendgrid import MailSendGrid
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from celery import Celery

from .config import Config

sql_db= SQLAlchemy()
nosql_db= MongoEngine()
mail= MailSendGrid()
bcrypt= Bcrypt()
migrate = Migrate()
jwt_manager= JWTManager()

celery = Celery(__name__, broker= Config.CELERY_BROKER_URL)

def create_app(config_class= Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    celery.conf.update(app.config)

    JWTManager(app)
    nosql_db.init_app(app)
    sql_db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt_manager.init_app(app)
    migrate.init_app(app, sql_db)

    from cloudbox.core.routes import core
    from cloudbox.auth.routes import auth
    from cloudbox.store.routes import store

    app.register_blueprint(core)
    app.register_blueprint(auth)
    app.register_blueprint(store)

    return app

from .models import User