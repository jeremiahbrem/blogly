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

class TagViewsTestCase(TestCase):
    """Tests views for Tag"""

    def setUp(self):
        """Add sample tag."""

        db.create_all()
        user = User(first_name="Steve", last_name="Rogers")
        tag = Tag(name="Marvel")
        post = Post(title="Avengers", content="We're coming for you, Thanos.", user=user)
        tag.posts.append(post)
        db.session.add_all([user, tag, post])
        db.session.commit()

        self.tag = tag

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        db.drop_all()

    def test_show_tags(self):
        """Testing if tag list page shows"""

        with app.test_client() as client:
            resp = client.get("/tags")
            html = resp.get_data(as_text=True)
            tags = Tag.query.all()

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Tag List", html)
            self.assertIn(tags[0].name, html)

    def test_show_add_tag(self):
        """Testing if create tag form shows"""

        with app.test_client() as client:
            resp = client.get("/tags/new")       
            html = resp.get_data(as_text=True)      

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Create Tag", html)

    def test_add_tag(self):
        """Testing if tag is added and shows on tag list"""

        with app.test_client() as client:
            d = {"name": "hero"}
            resp = client.post("/tags/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)       

            self.assertEqual(resp.status_code, 200)
            self.assertIn("hero", html)

    def test_add_tag_invalid(self):
        """Testing if correct response is given with empty inputs"""

        with app.test_client() as client:    
            d = {"name": ""}
            resp = client.post("/tags/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please enter tag name", html)

    def test_show_tag_details(self):
        """Testing if tag detail page shows correctly"""
        
        with app.test_client() as client:
            resp = client.get(f"/tags/{self.tag.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Marvel", html)
            self.assertIn("Avengers", html)

    def test_show_tag_edit(self):
        """Testing if tag edit form displays"""

        with app.test_client() as client:
            resp = client.get(f"/tags/{self.tag.id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Tag", html)
            self.assertIn(self.tag.name, html)

    def test_edit_tag(self):
        """Testing if tag is edited and shown on tag list"""

        with app.test_client() as client:
            d = {"name": "DC"}
            resp = client.post(f"/tags/{self.tag.id}/edit", data=d, follow_redirects=True)   
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)     
            self.assertIn("DC", html)

    def test_edit_tag_invalid(self):
        """Testing if correct response is given with empty inputs"""

        with app.test_client() as client:    
            d = {"name": ""}
            resp = client.post(f"/tags/{self.tag.id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please enter tag name", html)

    def test_delete_tag(self):
        """Testing if tag is deleted and removed from list"""

        with app.test_client() as client:
            resp = client.post(f"/tags/{self.tag.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Marvel", html)        

                


