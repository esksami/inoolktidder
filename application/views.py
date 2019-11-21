from flask import render_template
from flask_login import current_user

from application import app, db
from application.posts.models import Post

@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", post_count=Post.user_post_count(current_user.id))
    else:
        return render_template("index.html")