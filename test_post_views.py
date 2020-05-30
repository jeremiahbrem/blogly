from sqlalchemy import desc
from unittest import TestCase

from app import app
from models import db, User, Post, Tag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class PostViewsTestCase(TestCase):
    """Tests views for Post"""

    def setUp(self):
        """Add sample user and post."""

        db.create_all()
        user = User(first_name='Chris', last_name='Hemsworth', image_url='https://cdn1.thr.com/sites/default/files/imagecache/768x433/2017/11/thorragnarok59e8057250eb8-h_2017.jpg')
        post = Post(title="Mjolnir", content="I love my hammer.", user=user)
        db.session.add(user)
        db.session.add(post)
        db.session.commit()

        self.user_id = user.id
        self.post_id = post.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        db.drop_all()

    def test_show_recent(self):
        """Testing if home page shows recent posts"""

        with app.test_client() as client:
            recent = Post.query.order_by(desc("created_at")).limit(5).all()
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(recent[0].title, html)

    def test_show_post_form(self):
        """Testing if user edit form page displays"""

        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/posts/new") 
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>Create Post for Chris Hemsworth</h1>", html)        

    def test_add_post(self):
        """Testing if user post is added correctly"""

        with app.test_client() as client:
            d = {"title": "Asgard", "content": "I love my home", "user_id": self.user_id}
            resp = client.post(f"users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Asgard", html)

    def test_add_post_invalid(self):
        """Testing if correct response is given with empty inputs"""

        with app.test_client() as client:    
            d = {"title": "", "content": ""}
            resp = client.post(f"/users/{self.user_id}/posts/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please enter title and content", html)        

    def test_show_post(self):
        """Testing if post details show correctly"""

        with app.test_client() as client:
            tag = Tag(name="hero")
            post = Post.query.get_or_404(self.post_id)
            post.tags.append(tag)
            db.session.add_all([tag, post])
            db.session.commit()
            resp = client.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Chris Hemsworth", html)              
            self.assertIn("Mjolnir", html)   
            self.assertIn("I love my hammer.", html)
            self.assertIn("hero", html)

    def test_delete_post(self):
        """Testing if post is deleted and removed from user posts"""

        with app.test_client() as client:
            resp = client.post(f"/posts/{self.post_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Mjolnir", html)     

    def test_show_post_edit(self):
        """Testing if edit post form page shows"""

        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Post", html)
            self.assertIn("Mjolnir", html)

    def test_edit_post(self):
        """Testing if post is correctly edited"""

        d = {"title": "Asgard", "content": "I love my home"}
        with app.test_client() as client:
            resp = client.post(f"/posts/{self.post_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Asgard", html)
            self.assertIn("I love my home", html)

    def test_edit_post_invalid(self):
        """Testing if correct response is given with empty inputs"""

        with app.test_client() as client:    
            d = {"title": "", "content": ""}
            resp = client.post(f"/posts/{self.post_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please enter a title and content", html)
