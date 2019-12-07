from flask import redirect, render_template, request, url_for, request
from flask_login import login_required, current_user

from application import app, db
from application.utils import session_scope
from application.utils import roles_required

from application.posts.models import Post, PostLike, PostLikeValue
from application.posts.forms import PostForm

from application.auth.models import User

from application.comments.models import Comment
from application.comments.forms import CommentForm

from application.posts.utils.comment_tree import create_comment_tree

from contextlib import suppress

from sqlalchemy import and_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import bindparam, literal_column


@app.route("/", methods=["GET"])
def posts_index(page=1, per_page=10):
    with suppress(KeyError):
        page = int(request.args['page'])

    user_id = None

    if current_user and current_user.is_authenticated:
        user_id = current_user.id        

    postLikes = aliased(PostLike)
    postDislikes = aliased(PostLike)
    userLike = aliased(PostLike)

    with session_scope() as session:
        postCommentCount = (session
            .query(Post.id.label('post_id'),
                   db.func.count(Comment.post_id).label('comments'))
            .outerjoin(Comment, Comment.post_id == Post.id)
            .group_by(Post.id)).subquery()

        response = (session
            .query(Post,
                   postCommentCount.c.comments,
                   db.func.count(postLikes.value),
                   db.func.count(postDislikes.value),
                   userLike.value)
            .outerjoin(User, User.id == Post.account_id)
            .outerjoin(postCommentCount, postCommentCount.c.post_id == Post.id)
            .outerjoin(postLikes,
                       and_(postLikes.post_id == Post.id,
                            postLikes.value == PostLikeValue.like))
            .outerjoin(postDislikes,
                       and_(postDislikes.post_id == Post.id,
                            postDislikes.value == PostLikeValue.dislike))
            .outerjoin(userLike,
                       and_(userLike.post_id == Post.id,
                            userLike.account_id == user_id))
            .group_by(Post.id)
            .paginate(page=page, per_page=per_page, max_per_page=50))


        response = response

        posts = [post for post,
                          post.comments,
                          post.likes,
                          post.dislikes,
                          post.likeValue in response.items]

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
    user_id = None

    if current_user and current_user.is_authenticated:
        user_id = current_user.id 

    postLikes = aliased(PostLike)
    postDislikes = aliased(PostLike)
    userLike = aliased(PostLike)

    with session_scope() as session:
        postCommentCount = (session
            .query(Post.id.label('post_id'),
                 db.func.count(Comment.post_id).label('comments'))
            .outerjoin(Comment, Comment.post_id == Post.id)
            .group_by(Post.id)).subquery()

        response = (session
            .query(Post,
                   postCommentCount.c.comments,
                   db.func.count(postLikes.value),
                   db.func.count(postDislikes.value),
                   userLike.value)
            .outerjoin(User, User.id == Post.account_id)
            .outerjoin(postCommentCount, postCommentCount.c.post_id == Post.id)
            .outerjoin(postLikes,
                       and_(postLikes.post_id == Post.id,
                            postLikes.value == PostLikeValue.like))
            .outerjoin(postDislikes,
                       and_(postDislikes.post_id == Post.id,
                            postDislikes.value == PostLikeValue.dislike))
            .outerjoin(userLike,
                       and_(userLike.post_id == Post.id,
                            userLike.account_id == user_id))
            .group_by(Post.id)
            .filter(Post.id == post_id)
            .first())

        (post,
         post.comments,
         post.likes,
         post.dislikes,
         post.likeValue) = response

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

@app.route("/posts/like/<post_id>/", methods=["POST"])
@login_required
def posts_like(post_id):
    with session_scope() as session:
        oldLike = (session
            .query(PostLike)
            .filter(PostLike.post_id == post_id,
                    PostLike.account_id == current_user.id)
            .first())

        newLike = PostLike(
            value=PostLikeValue.like,
            post_id=post_id,
            account_id=current_user.id
        )

        if oldLike:
            session.delete(oldLike)
            session.flush()

        session.add(newLike)
        session.commit()

    return redirect(url_for("posts_index"))


@app.route("/posts/unlike/<post_id>/", methods=["POST"])
@login_required
def posts_undo_like(post_id):
    post_like = (PostLike.query
        .filter(PostLike.post_id == post_id,
                PostLike.account_id == current_user.id)
        .first())

    if not post_like:
        return redirect(url_for("posts_index"))

    with session_scope() as session:
        session.delete(post_like)
        session.commit()

    return redirect(url_for("posts_index"))


@app.route("/posts/dislike/<post_id>/", methods=["POST"])
@login_required
def posts_dislike(post_id):
    with session_scope() as session:
        oldDislike = (session
            .query(PostLike)
            .filter(PostLike.post_id == post_id,
                    PostLike.account_id == current_user.id)
            .first())

        newDislike = PostLike(
            value=PostLikeValue.dislike,
            post_id=post_id,
            account_id=current_user.id
        )

        if oldDislike:
            session.delete(oldDislike)
            session.flush()

        session.add(newDislike)
        session.commit()

    return redirect(url_for("posts_index"))


@app.route("/posts/undislike/<post_id>/", methods=["POST"])
@login_required
def posts_undo_dislike(post_id):
    post_dislike = (PostLike.query
        .filter(PostLike.post_id == post_id,
                PostLike.account_id == current_user.id)
        .first())

    if not post_dislike:
        return redirect(url_for("posts_index"))

    with session_scope() as session:
        session.delete(post_dislike)
        session.commit()

    return redirect(url_for("posts_index"))