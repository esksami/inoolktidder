from flask import redirect, render_template, request, url_for
from flask_login import login_required, current_user

from application import app, db
from application.utils import session_scope
from application.utils import roles_required

from application.comments.models import Comment
from application.comments.forms import CommentForm

from application.posts.models import Post

from application.auth.models import User


@app.route("/<post_id>/comments/create", defaults={'comment_id': None}, methods=["GET", "POST"])
@app.route("/<post_id>/comments/create/<comment_id>", methods=["GET", "POST"])
@login_required
@roles_required('APPROVED')
def comments_create(post_id, comment_id):
    if request.method == 'GET':
        redirect(f'{url_for("posts_details", post_id=post_id)}#{comment_id or ""}')

    form = CommentForm(request.form)

    if not form.validate():
        redirect(url_for("posts_details", post_id=post_id))

    parent = Comment.query.get(comment_id) if comment_id else None

    if parent and not parent.post_id == post_id:
        redirect(url_for("posts_details", post_id=post_id))

    comment = Comment(form.content.data)
    comment.account_id = current_user.id
    comment.post_id = post_id
    comment.parent_id = comment_id

    with session_scope() as session:
        session.add(comment)
        session.commit()

        return redirect(f'{url_for("posts_details", post_id=post_id)}#{comment.id}')

@app.route("/<post_id>/comments/delete/<comment_id>/", methods=["GET", "POST"])
@login_required
def comments_delete(post_id, comment_id):
    if request.method == 'GET':
        redirect(url_for("posts_details", post_id=post_id))

    with session_scope() as session:
        comment = Comment.query.get(comment_id)

        if comment.account_id != current_user.id:
            return redirect(url_for("posts_details", post_id=comment.post_id))

        comment.deleted = True

        session.commit()

        return redirect(f'{url_for("posts_details", post_id=comment.post_id)}#{comment.id}')