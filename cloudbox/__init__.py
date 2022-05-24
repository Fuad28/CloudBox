from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt

from .config import Config


db= MongoEngine()
login_manager= LoginManager()
login_manager.login_view= 'users.login'
mail= Mail()
bcrypt= Bcrypt()



def create_app(config_class= Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from cloudbox.main.routes import main
    from cloudbox.users.routes import users

    app.register_blueprint(main, url_prefix= '/')
    app.register_blueprint(users, url_prefix= '/users')

    return app




    # <div class="col-lg-12"></div>
    #                           <div class="floating-label form-group">
    #                              {% if form.country.errors %}
    #                                 {{ form.country(class="floating-input form-control is-invalid", placeholder=" ", type="text") }}
    #                                 <div class="invalid-feedback">
    #                                    {% for error in form.country.errors %}
    #                                        <span>{{ error }}</span>
    #                                    {% endfor %}
    #                                </div>
    #                              {% else %}
    #                                {{ form.country(class="floating-input form-control", placeholder=" ", type="text") }}
    #                              {% endif %}
    #                              <label>Country</label>
    #                           </div>