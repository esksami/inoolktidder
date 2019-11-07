from application import app, db
from flask import redirect, render_template, request, url_for
from application.posts.models import Post

@app.route("/posts", methods=["GET"])
def posts_index():
    return render_template("posts/list.html", posts=Post.query.all())

@app.route("/posts/new/")
def posts_form():
    return render_template("posts/new.html")

@app.route("/posts/edit/<post_id>/")
def posts_edit_form(post_id):
    return render_template("posts/edit.html", post=Post.query.get(post_id))

@app.route("/posts/edit/<post_id>/", methods=["POST"])
def posts_edit(post_id):
    title = request.form.get("title")
    content = request.form.get("content")

    post = Post.query.get(post_id)
    post.title = title
    post.content = content
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
    title = request.form.get("title")
    content = request.form.get("content")

    post = Post(title, content)

    db.session().add(post)
    db.session().commit()
  
    return redirect(url_for("posts_index"))