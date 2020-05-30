from flask import Flask, render_template, request, redirect, flash, session
from sqlalchemy import desc
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

db.create_all()

from flask_debugtoolbar import DebugToolbarExtension
app.config['SECRET_KEY'] = "dfg1df65g1df65"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route("/")
def redirect_users():
    """Shows recent blogly posts"""

    recent = Post.query.order_by(desc("created_at")).limit(5).all()

    return render_template("posts/recent_posts.html", posts=recent)

@app.route("/users")
def list_users():
    """Displays list of users"""

    users = User.query.order_by("last_name").all()
    return render_template("users/user_list.html", users=users)

@app.route("/users/<int:user_id>")
def show_details(user_id):
    """Shows details of a user"""

    user = User.query.get_or_404(user_id)

    return render_template("users/user_details.html", user=user, posts=user.posts)

@app.route("/users/new")
def create_user():
    """Returns create user form page"""

    return render_template("users/create_user.html")

@app.route("/users/new", methods=["POST"])
def add_user():
    """Adds new user to database and redirects to user details page"""


    first = request.form['first_name']
    last = request.form['last_name']
    image = request.form['image_url']
    
    if not first or not last:
        flash("Please enter first and last name.")
        return redirect("/users/new")
    
    user = User(first_name=first, last_name=last)
    
    if image:
        user.image_url = image

    db.session.add(user)
    db.session.commit()

    return redirect("/users")    

@app.route("/users/<int:user_id>/edit") 
def show_edit_form(user_id):
    """Returns edit form page for user"""

    user = User.query.get_or_404(user_id)

    return render_template("users/edit_user.html", user=user)

@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user(user_id):
    """Edits user and redirects to user list page"""

    user = User.query.get_or_404(user_id)
    
    first = request.form['first_name']
    last = request.form['last_name']
    image = request.form['image_url']
    
    if not first or not last:
        flash("Please enter first and last name.")
        return redirect(f"/users/{user.id}/edit")
    
    user.first_name = first
    user.last_name = last
    
    if image:
        user.image_url = image

    db.session.add(user)
    db.session.commit()

    return redirect("/users")

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Deletes user and redirects to user list page"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

@app.route("/users/<int:user_id>/posts/new") 
def show_post_form(user_id):
    """Returns create form page for user"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    return render_template("posts/create_post.html", user=user, tags=tags)    

@app.route("/users/<int:user_id>/posts/new", methods=["POST"])    
def add_post(user_id):
    """Adds user post and redirects to user detail page"""

    title = request.form['title']
    content = request.form['content']
    tags = request.form.getlist('tag')
    user = User.query.get_or_404(user_id)

    if not title or not content:
        flash("Please enter title and content.")
        return redirect(f"/users/{user.id}/posts/new")

    post = Post(title=title, content=content, user=user)

    if tags:
        for tag in tags:
            post.tags.append(Tag.query.filter(Tag.name==tag).one())

    db.session.add(post)
    db.session.commit()

    user = User.query.get_or_404(user_id)

    return redirect(f"/users/{user_id}")

@app.route("/posts/<int:post_id>") 
def show_post(post_id):
    """Shows post details page"""

    post = Post.query.get_or_404(post_id)
    user = post.user
    
    return render_template("posts/post_details.html", post=post, user=user)

@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """Deletes user post and redirects to user details page"""

    post = Post.query.get_or_404(post_id)
    user = post.user
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{user.id}")

@app.route("/posts/<int:post_id>/edit")
def show_post_edit(post_id):
    """Displays edit post form page"""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()

    return render_template("posts/edit_post.html", post=post, tags=tags)

@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post(post_id):
    """Edits user post and returns to post details page"""

    post = Post.query.get_or_404(post_id)

    title = request.form["title"]
    content = request.form["content"]
    tags = request.form.getlist("tag")
    post.tags = []
    if tags:
        for tag in tags:
            post.tags.append(Tag.query.filter(Tag.name==tag).one())

    if not title or not content:
        flash("Please enter a title and content")
        return redirect(f"/posts/{post.id}/edit")

    post.title = title
    post.content = content
    db.session.add(post)    
    db.session.commit()

    return redirect(f"/posts/{post_id}")

@app.route("/tags")
def show_tags():
    """Shows tag list page"""

    tags = Tag.query.all()

    return render_template("tags/tag_list.html", tags=tags)

@app.route("/tags/new")    
def show_add_tag():
    """Returns create tag form page"""

    return render_template("tags/create_tag.html")

@app.route("/tags/new", methods=["POST"])    
def add_tag():
    """Adds new tag and returns tag list page"""

    tag_name = request.form["name"]

    if not tag_name:
        flash("Please enter tag name")
        return redirect("/tags/new")

    tag = Tag(name=tag_name)
    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")

@app.route("/tags/<int:tag_id>")
def show_tag_details(tag_id):
    """Shows tag detail page"""

    tag = Tag.query.get_or_404(tag_id)

    return render_template("tags/tag_details.html", tag=tag)

@app.route("/tags/<int:tag_id>/edit")
def show_tag_edit(tag_id):
    """Returns edit tag form page"""

    tag = Tag.query.get_or_404(tag_id)

    return render_template("tags/edit_tag.html", tag=tag)

@app.route("/tags/<int:tag_id>/edit", methods=["POST"]) 
def edit_tag(tag_id):
    """Edits tag and returns to tag details page"""

    tag = Tag.query.get_or_404(tag_id)
    tag_name = request.form["name"]

    if not tag_name:
        flash("Please enter tag name")
        return redirect(f"/tags/{tag_id}/edit")

    tag.name = tag_name
    db.session.add(tag)
    db.session.commit()

    return redirect(f"/tags/{tag_id}")

@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag(tag_id):
    """Deletes tag and redirects to user details page"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect(f"/tags")    


    

