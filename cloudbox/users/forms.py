from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from cloudbox.models import User

class RegistrationForm(FlaskForm):
    #personal
    first_name= StringField("First name", validators= [DataRequired(), Length(min=2, max=20)])
    last_name= StringField("Last name", validators= [DataRequired(), Length(min=2, max=20)])
    middle_name= StringField("Middle name", validators= [DataRequired(), Length(min=2, max=20)])
    email= StringField("Email", validators= [DataRequired(), Email()])
    country= StringField("Country", validators= [DataRequired(), Length(min=2, max=50)])
    password= PasswordField("password", validators= [DataRequired(), Length(min=4, max=100)])
    confirm_password= PasswordField("confirm_password", validators= [DataRequired(), EqualTo('password')])
    date_of_birth= DateTimeField("Date of Birth", validators= [DataRequired()], format= "%Y-%m-%dT%H:%M:%")
    profile_pict= FileField("Profile picture", validators= [FileAllowed(["jpg", "png"])])

    #security question
    security_quest= StringField("Security question", validators= [DataRequired(), Length(min=2, max=255)])
    security_ans= StringField("Answer", validators= [DataRequired(), Length(min=2, max=30)])

    #recovery
    recovery_mail= StringField("Email", validators= [DataRequired(), Email()])
    recovery_no= StringField("Recovery contact", validators= [DataRequired(), Length(min=11, max=14)])

    submit= SubmitField("Sign Up")

    def validate_email(self, email):
        user= User.objects.filter(email=email.data).first()
        if user:
            raise ValidationError("This email has been taken by another user! Try another")


class LoginForm(FlaskForm):
    email= StringField("Email", validators= [DataRequired(), Email()])
    password= PasswordField("password", validators= [DataRequired()])
    remember= BooleanField("remember me")

    submit= SubmitField("Login")