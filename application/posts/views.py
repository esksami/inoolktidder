from flask import redirect, render_template, request, url_for, request
from flask_login import login_required, current_user

from application import app, db
from application.utils import session_scope
from application.utils import roles_required

from application.posts.models import Post
from application.posts.forms import PostForm

from application.auth.models import User

from application.comments.models import Comment
from application.comments.forms import CommentForm

from application.posts.utils.comment_tree import create_comment_tree

from contextlib import suppress

@app.route("/", methods=["GET"])
def posts_index(page=1, per_page=10):
    with suppress(KeyError):
        page = int(request.args['page'])

    with session_scope() as session:
        response = (session
              .query(Post, db.func.count(Comment.post_id))
              .join(User, User.id == Post.account_id)
              .outerjoin(Comment, Comment.post_id == Post.id)
              .group_by(Post.id)
              .paginate(page=page, per_page=per_page, max_per_page=50))

        posts = []

        for post, commentCount in response.items:
            post.comments = commentCount

            posts.append(post)

        first = max(1, response.page - 2)
        last = min(response.pages, response.page + 2) + 1
        page_range = list(range(first, last))

        return render_template(
            "posts/list.html",
            posts=posts,
            page_range=page_range,
            pagination=response
        )

@app.route("/submit")
@login_required
def posts_submit_form():
    return render_template("posts/submit.html", form=PostForm())

@app.route("/submit", methods=["POST"])
@login_required
@roles_required('APPROVED')
def posts_submit():
    form = PostForm(request.form)

    if not form.validate():
        return render_template("posts/submit.html", form=form)

    with session_scope() as session:
        post = Post(form.title.data, form.content.data)
        post.account_id = current_user.id

        session.add(post)
        session.commit()
  
    return redirect(url_for("posts_index"))

@app.route("/edit/<post_id>/")
@login_required
def posts_edit_form(post_id):
    post = Post.query.get(post_id)

    if post.account_id != current_user.id:
        return render_template("posts/details.html", post=post,
                        error="You can only edit your own posts.")

    return render_template("posts/edit.html",
                           post=post,
                           form=PostForm())

@app.route("/edit/<post_id>/", methods=["POST"])
@login_required
def posts_edit(post_id):
    form = PostForm(request.form)
    
    post = Post.query.get(post_id)

    if post.account_id != current_user.id:
        return render_template(
            "posts/details.html",
            post=post,
            error="You can only edit your own posts.")

    post.title = form.title.data
    post.content = form.content.data

    if not form.validate():
        return render_template(
            "posts/edit.html",
            post=post,
            form=form
        )

    with session_scope() as session:
        session.commit()
  
    return redirect(url_for("posts_details", post_id=post_id))

@app.route("/delete/<post_id>/", methods=["POST"])
@login_required
def posts_delete(post_id):
    with session_scope() as session:
        post = Post.query.get(post_id)

        if post.account_id != current_user.id:
            return render_template("posts/details.html", post=post,
                            error="You can't delete someone elses post.")

        session.delete(post)
        session.commit()

    return redirect(url_for("posts_index"))

@app.route("/<post_id>/")
def posts_details(post_id):
    with session_scope() as session:
        post, post.comments = (session
            .query(Post, db.func.count(Comment.post_id))
            .join(User, User.id == Post.account_id)
            .outerjoin(Comment, Comment.post_id == Post.id)
            .group_by(Post.id)
            .filter(Post.id == post_id)
            .first())

        comments = (session
            .query(Comment)
            .filter(Comment.post_id == post_id)
            .join(User, User.id == Comment.account_id)
            .all())

        return render_template(
            "posts/details.html",
            post=post,
            commentTree=create_comment_tree(comments),
            form=CommentForm()
        )

@app.route("/posts/<post_id>/", methods=["POST"])
@login_required
def posts_like(post_id):
    post = Post.query.get(post_id)
    post.likes += 1

    with session_scope() as session:
        session.commit()

    return redirect(url_for("posts_index"))

