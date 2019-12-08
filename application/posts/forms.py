from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField
from wtforms.validators import Length

class PostForm(FlaskForm):
    title = StringField("Title", [
    	Length(
    		min=3,
    		max=512,
    		message='Title must be between 3 and 512 characters'
    	)
    ])
    content = TextAreaField("Content", [
    	Length(
    		min=0,
    		max=8192,
    		message='Content must be less than 8192 characters'
    	)
    ])

    class Meta:
        csrf = False