from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, TextField, validators

class PostForm(FlaskForm):
    title = StringField("Title", [validators.Length(min=2, max=512)])
    content = TextField("Content", [validators.Length(min=0, max=8192)])

    class Meta:
        csrf = False