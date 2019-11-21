from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators
  
class LoginForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=3, max=64)])
    password = PasswordField('Password', [
        validators.DataRequired(message="Please enter a password."),
    ])
    # confirmPassword = PasswordField('Repeat Password', [
    #     EqualTo(password, message='Passwords must match.')
    # ])
  
    class Meta:
        csrf = False