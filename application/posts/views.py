from contextlib import suppress

from flask import redirect, render_template, request, url_for, request
from flask_login import login_required, current_user

from sqlalchemy import asc, desc, text
from sqlalchemy.orm import aliased

from application import app, db
from application.utils import session_scope, roles_required

from application.auth.models import User

from application.comments.models import Comment
from application.comments.forms import CommentForm

from application.posts.models import Post, PostLike, PostLikeValue
from application.posts.forms import PostForm
from application.posts.query import posts_with_aggregates
from application.posts.utils import create_comment_tree


@app.route('/', methods=['GET'])
def posts_index(page=1, per_page=10, sort='popular'):
    user_id = None

    if current_user and current_user.is_authenticated:
        user_id = current_user.id

    pagination_kwargs = {
        'page': int(request.args.get('page') or page),
        'per_page': int(request.args.get('per_page') or per_page),
        'max_per_page': 50
    }

    sort = request.args.get('sort') or sort
    queryString = request.args.get('query')

    with session_scope() as session:
        query = posts_with_aggregates(session, user_id=user_id)

        if queryString:
            query = query.filter(Post.title.ilike('%{}%'.format(queryString)))

        if sort == 'newest':
            query = query.order_by(desc(Post.date_created))
        elif sort == 'oldest':
            query = query.order_by(asc(Post.date_created))
        elif sort == 'popular':
            query = query.order_by(desc(text('popularity')))

        pagination = None
        items = []

        with suppress(Exception):
            pagination = query.paginate(**pagination_kwargs)
            items = pagination.items

        posts = [post for post,
                          post.comments,
                          post.likes,
                          post.dislikes,
                          post.popularity,
                          post.userLike in items]

        page_range = None

        if pagination:
            first = max(1, pagination.page - 2)
            last = min(pagination.pages, pagination.page + 2) + 1
            page_range = list(range(first, last))

        return render_template(
            'posts/list.html',
            posts=posts,
            page_range=page_range,
            pagination=pagination
        )

@app.route('/submit')
@login_required
def posts_submit_form():
    return render_template('posts/submit.html', form=PostForm())

@app.route('/submit', methods=['POST'])
@login_required
@roles_required('APPROVED')
def posts_submit():
    form = PostForm(request.form)

    if not form.validate():
        return render_template('posts/submit.html', form=form)

    with session_scope() as session:
        post = Post(form.title.data, form.content.data)
        post.account_id = current_user.id

        session.add(post)
        session.commit()
  
    return redirect(url_for('posts_index'))

@app.route('/edit/<post_id>/')
@login_required
def posts_edit_form(post_id):
    post = Post.query.get(post_id)

    if post.account_id != current_user.id:
        return render_template(
            'posts/details.html',
            post=post,
            error='You can only edit your own posts.'
        )

    return render_template(
        'posts/edit.html',
        post=post,
        form=PostForm()
    )

@app.route('/edit/<post_id>/', methods=['POST'])
@login_required
def posts_edit(post_id):
    form = PostForm(request.form)
    
    post = Post.query.get(post_id)

    if post.account_id != current_user.id:
        return render_template(
            'posts/details.html',
            post=post,
            error='You can only edit your own posts.'
        )

    post.title = form.title.data
    post.content = form.content.data

    if not form.validate():
        return render_template(
            'posts/edit.html',
            post=post,
            form=form
        )

    with session_scope() as session:
        session.commit()
  
    return redirect(url_for('posts_details', post_id=post_id))

@app.route('/delete/<post_id>/', methods=['POST'])
@login_required
def posts_delete(post_id):
    with session_scope() as session:
        post = Post.query.get(post_id)

        if post.account_id != current_user.id:
            return render_template(
                'posts/details.html',
                post=post,
                error='You can\'t delete someone elses post.'
            )

        session.delete(post)
        session.commit()

    return redirect(url_for('posts_index'))

@app.route('/<post_id>/')
def posts_details(post_id):
    user_id = None

    if current_user and current_user.is_authenticated:
        user_id = current_user.id 

    with session_scope() as session:
        query = (posts_with_aggregates(session, user_id=user_id)
            .filter(Post.id == post_id))
        response = query.first()

        (post,
         post.comments,
         post.likes,
         post.dislikes,
         post.popularity,
         post.userLike) = response

        comments = (session
            .query(Comment)
            .filter(Comment.post_id == post_id)
            .outerjoin(User, User.id == Comment.account_id)
            .limit(100)
            .all())

        return render_template(
            'posts/details.html',
            post=post,
            commentTree=create_comment_tree(comments),
            form=CommentForm()
        )

@app.route('/posts/like/<post_id>/', methods=['POST'])
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

    return redirect(request.referrer)

@app.route('/posts/unlike/<post_id>/', methods=['POST'])
@login_required
def posts_undo_like(post_id):
    post_like = (PostLike.query
        .filter(PostLike.post_id == post_id,
                PostLike.account_id == current_user.id)
        .first())

    if not post_like:
        return redirect(request.referrer)

    with session_scope() as session:
        session.delete(post_like)
        session.commit()

    return redirect(request.referrer)

@app.route('/posts/dislike/<post_id>/', methods=['POST'])
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

    return redirect(request.referrer)

@app.route('/posts/undislike/<post_id>/', methods=['POST'])
@login_required
def posts_undo_dislike(post_id):
    post_dislike = (PostLike.query
        .filter(PostLike.post_id == post_id,
                PostLike.account_id == current_user.id)
        .first())

    if not post_dislike:
        return redirect(request.referrer)

    with session_scope() as session:
        session.delete(post_dislike)
        session.commit()

    return redirect(request.referrer)