from unittest import TestCase
import datetime

from app import app
from models import db, User, Post

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Tests for model for Users."""

    def setUp(self):
        """Clean up any existing users."""

        db.create_all()
        user = User(first_name="Bob", last_name="Smith")
        db.session.add(user)
        db.session.commit()
        self.user = user

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        db.drop_all()

    def test_full_name(self):
        """Testing is user full name property displays correctly"""

        self.assertEqual(self.user.full_name, "Bob Smith")

    def test_friendly_datetime(self):    
        """Testing if correct post.created_at datetime is shown in user friendly form"""
        
        
        p = Post(title="Hi", content="Hey", user=self.user)
        db.session.add(p)
        db.session.commit()
        d = datetime.datetime.now().strftime("%b %d, %Y %I:%M%p")
        
        self.assertEqual(p.friendly_datetime(), d)