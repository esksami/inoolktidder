from flask import redirect, render_template, request, url_for
from flask_login import login_required, current_user

from application import app, db

from application.comments.models import Comment
from application.comments.forms import CommentForm

from application.auth.models import User


@app.route("/<post_id>/comments/create", defaults={'comment_id': None}, methods=["POST"])
@app.route("/<post_id>/comments/create/<comment_id>", methods=["POST"])
@login_required
def comments_create(post_id, comment_id):
    form = CommentForm(request.form)

    if not form.validate():
        return render_template("comments/submit.html", form=form)

    comment = Comment(form.content.data)
    comment.account_id = current_user.id
    comment.post_id = post_id
    comment.parent_id = comment_id

    db.session().add(comment)
    db.session().commit()

    return redirect(url_for("posts_details", post_id=post_id))