from functools import wraps

from flask import url_for, redirect, request, render_template
from flask_login import current_user

from application import login_manager
from application.posts.models import Post


def validate_post_id(f):
    @wraps(f)
    def decorator(*args, post_id, **kwargs):
        post = Post.query.get(post_id)

        if not post:
            return redirect(url_for('posts_index'))

        return f(*args, post_id=post_id, **kwargs)
    return decorator


def validate_post_owner(f):
    @wraps(f)
    def decorator(*args, post_id, **kwargs):
        post = Post.query.get(post_id)

        if not post:
            return redirect(url_for('posts_index'))

        if post.account_id != current_user.id:
            return redirect(url_for('posts_index', post_id=post_id))

        return f(*args, post_id=post_id, **kwargs)
    return decorator