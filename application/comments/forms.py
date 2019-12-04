from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, TextAreaField, validators

class CommentForm(FlaskForm):
    content = TextAreaField("Content", [validators.Length(min=0, max=4096)])

    class Meta:
        csrf = False