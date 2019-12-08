from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import Length

class CommentForm(FlaskForm):
    content = TextAreaField("Content", [
    	Length(
    		min=0, 
    		max=4096,
    		message='Content must be less than 4096 characters'
    	)
    ])

    class Meta:
        csrf = False