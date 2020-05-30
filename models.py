from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """Creates User for Blogly app"""

    __tablename__ =  "users"

    id = db.Column(db.Integer,
                   primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False, default="https://img.icons8.com/ultraviolet/40/000000/full-image.png")
    posts = db.relationship("Post", cascade="all, delete-orphan")
    
    def __repr__(self):
        """Show info about user."""

        return f"<User {self.id} {self.full_name}>"

    @property
    def full_name(self):
        """Sets property that returns user full name"""

        return f"{self.first_name} {self.last_name}"

class Post(db.Model):
    """Model for creating user posts"""

    __tablename__ =  "posts"     

    id = db.Column(db.Integer,
                   primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)
    user = db.relationship("User")

    def __repr__(self):
        """Show info about post."""

        return f"<Post {self.id} {self.title}>"                        

    def friendly_datetime(self):
        """Returns a user friendly post.created_at datetime"""
        
        return self.created_at.strftime("%b %d, %Y %I:%M%p")

class Tag(db.Model):
    """Model for creating tags"""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    
    posts = db.relationship("Post",
                            secondary="post_tag",
                            cascade="all, delete",
                            backref="tags")

    def __repr__(self):
        """Show info about tag."""

        return f"<Tag {self.id} {self.name}>"

class PostTag(db.Model):
    """Model for mapping tags to posts"""

    __tablename___ = "post_tags"      


    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        primary_key=True)

    tag_id = db.Column(db.Integer,
                       db.ForeignKey('tags.id'),
                       primary_key=True)  
                            

                                    
    