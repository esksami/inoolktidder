from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', [
    	Length(min=3, max=64)
    ])
    password = PasswordField('Password', [
        DataRequired(message='Please enter a password.'),
    ])
  
    class Meta:
        csrf = False

class SignUpForm(FlaskForm):
    username = StringField('Username', [
    	Length(min=3, max=64,
    		message='Username must be between 3 and 64 characters'),
    	DataRequired()
    ])
    password = PasswordField('Password', [
    	Length(min=3, max=128,
    		message='Username must be between 3 and 128 characters'),
        DataRequired(),
    ])
    confirmPassword = PasswordField('Repeat Password', [
        EqualTo('password', message='Passwords must match.'),
        DataRequired()
    ])
  
    class Meta:
        csrf = False