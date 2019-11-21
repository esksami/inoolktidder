from application import app, db
from flask import redirect, render_template, request, url_for
from application.posts.models import Post
from application.posts.forms import PostForm


@app.route("/posts", methods=["GET"])
def posts_index():
    return render_template("posts/list.html", posts=Post.query.all())

@app.route("/posts/new/")
def posts_form():
    return render_template("posts/new.html", form=PostForm())

@app.route("/posts/edit/<post_id>/")
def posts_edit_form(post_id):
    return render_template("posts/edit.html",
                           post=Post.query.get(post_id),
                           form=PostForm())

@app.route("/posts/edit/<post_id>/", methods=["POST"])
def posts_edit(post_id):
    form = PostForm(request.form)

    post = Post.query.get(post_id)
    post.title = form.title.data
    post.content = form.content.data

    if not form.validate():
        return render_template("posts/edit.html",
                               post=post,
                               form=form)

    db.session().commit()
  
    return redirect(url_for("posts_details", post_id=post_id))

@app.route("/posts/<post_id>/")
def posts_details(post_id):
    return render_template("posts/details.html", post=Post.query.get(post_id))

@app.route("/posts/<post_id>/", methods=["POST"])
def posts_like(post_id):

    post = Post.query.get(post_id)
    post.likes += 1
    db.session().commit()

    return redirect(url_for("posts_index"))

@app.route("/posts/", methods=["POST"])
def posts_create():
    form = PostForm(request.form)

    if not form.validate():
        return render_template("posts/new.html", form=form)

    post = Post(form.title.data, form.content.data)

    db.session().add(post)
    db.session().commit()
  
    return redirect(url_for("posts_index"))