from flask import redirect, render_template, request, url_for
from flask_login import login_required, current_user

from application import app, db

from application.posts.models import Post
from application.posts.forms import PostForm

from application.auth.models import User

from application.comments.models import Comment
from application.comments.forms import CommentForm



@app.route("/", methods=["GET"])
def posts_index():
    posts = db.session().query(Post).join(User, User.id == Post.account_id).all()

    return render_template("posts/list.html", posts=posts)

@app.route("/submit")
@login_required
def posts_submit_form():
    return render_template("posts/submit.html", form=PostForm())

@app.route("/submit", methods=["POST"])
@login_required
def posts_submit():
    form = PostForm(request.form)

    if not form.validate():
        return render_template("posts/submit.html", form=form)

    post = Post(form.title.data, form.content.data)
    post.account_id = current_user.id

    db.session().add(post)
    db.session().commit()
  
    return redirect(url_for("posts_index"))

@app.route("/edit/<post_id>/")
@login_required
def posts_edit_form(post_id):
    post = Post.query.get(post_id)

    if post.account_id != current_user.id:
        return render_template("posts/details.html", post=post,
                        error="You can only edit your own posts.")

    return render_template("posts/edit.html",
                           post=Post.query.get(post_id),
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
        return render_template("posts/edit.html", post=post, form=form)

    db.session().commit()
  
    return redirect(url_for("posts_details", post_id=post_id))

@app.route("/delete/<post_id>/", methods=["POST"])
@login_required
def posts_delete(post_id):
    post = Post.query.get(post_id)

    if post.account_id != current_user.id:
        return render_template("posts/details.html", post=post,
                        error="You can't delete someone elses post.")

    db.session().delete(post)
    db.session().commit()

    return redirect(url_for("posts_index"))

@app.route("/<post_id>/")
def posts_details(post_id):
    comments = Comment.query.filter(Comment.post_id == post_id).join(User, User.id == Comment.account_id).all()
    commentTree = comment_tree(comments)

    return render_template(
        "posts/details.html",
        post=Post.query.get(post_id),
        comments=comments,
        commentTree=commentTree,
        form=CommentForm()
    )

@app.route("/posts/<post_id>/", methods=["POST"])
@login_required
def posts_like(post_id):
    post = Post.query.get(post_id)
    post.likes += 1
    db.session().commit()

    return redirect(url_for("posts_index"))

def comment_tree(comments):
    commentsByParentId = comments_by_parent_id(comments)
    roots = []

    for rootComment in [c for c in comments if c.parent_id is None]:
        root = CommentNode(
            comment=rootComment,
            **rootComment.__dict__)
        print(root.__dict__)
        root.children = populate(root, commentsByParentId)

        roots.append(root)

    return roots

def populate(node, commentsByParentId):
    try:
        comments = commentsByParentId[node.id]
    except KeyError:
        return []

    children = []

    for comment in comments:
        node = CommentNode(
            comment=comment,
            **comment.__dict__)
        node.children = populate(node, commentsByParentId)

        children.append(node)

    return children

from itertools import groupby

def comments_by_parent_id(comments):
    childComments = [c for c in comments if c.parent_id is not None]
    sortedComments = sorted(childComments, key=lambda c: c.parent_id)
    groups = groupby(sortedComments, key=lambda c: c.parent_id)
    return {parent_id: list(children) for parent_id, children in groups}

class CommentNode:
    def __init__(self, comment, children = [], **kwargs):
        self.comment = comment
        self.children = children

        for key, value in kwargs.items():
          setattr(self, key, value)