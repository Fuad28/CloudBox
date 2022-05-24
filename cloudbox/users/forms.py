from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from cloudbox.models import User

class RegistrationForm(FlaskForm):
    #personal
    first_name= StringField("First name", validators= [DataRequired(), Length(min=2, max=20)])
    last_name= StringField("Last name", validators= [DataRequired(), Length(min=2, max=20)])
    middle_name= StringField("Middle name", validators= [Optional(), Length(min=2, max=20)])
    phone= StringField("Phone", validators= [Optional(), Length(min=2, max=20)])
    email= StringField("Email", validators= [DataRequired(), Email()])
    country= SelectField("Country", validators= [Optional()], choices= [('abc', 'ABC'), ('de', 'DE'), ('fg', "FG")])
    password= PasswordField("password", validators= [DataRequired(), Length(min=4, max=100)])
    date_of_birth= DateTimeField("Date of Birth", format= "%Y-%m-%dT%H:%M:%")
    profile_pict= FileField("Profile picture", validators= [Optional(), FileAllowed(["jpg", "png"])])

    #security question
    security_quest= StringField("Security question", validators= [Optional(), Length(min=2, max=255)])
    security_ans= StringField("Answer", validators= [Optional(), Length(min=2, max=30)])

    #recovery
    recovery_mail= StringField("Email", validators= [Optional(), Email()])
    recovery_no= StringField("Recovery contact", validators= [Optional(), Length(min=11, max=14)])

    submit= SubmitField("Sign Up")

    def validate_email(self, email):
        user= User.objects.filter(email=email.data).first()
        if user:
            raise ValidationError("This email has been taken by another user! Try another")


class LoginForm(FlaskForm):
    email= StringField("Email", validators=[DataRequired(), Email()])
    password= StringField("Password", validators=[DataRequired()])
    remember= BooleanField("remember me")

    submit= SubmitField("Login")