from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from cloudbox.models import User

class LoginForm(FlaskForm):
    email= StringField("Email", validators= [DataRequired(), Email()])
    password= PasswordField("password", validators= [DataRequired()])
    remember= BooleanField("remember me")

    submit= SubmitField("Login")