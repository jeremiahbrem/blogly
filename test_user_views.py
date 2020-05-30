from unittest import TestCase

from app import app
from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class UserViewsTestCase(TestCase):
    """Tests views for User."""

    def setUp(self):
        """Add sample user."""

        db.create_all()
        user = User(first_name='Chris', last_name='Hemsworth', image_url='https://cdn1.thr.com/sites/default/files/imagecache/768x433/2017/11/thorragnarok59e8057250eb8-h_2017.jpg')
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        db.drop_all()

    def test_list_users(self):
        """Testing if home page shows with user list"""

        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Chris Hemsworth", html)

    def test_show_details(self):
        """Testing if user detail page shows correctly"""

        with app.test_client() as client:
            resp = client.get(f"users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Chris Hemsworth", html)              
            self.assertIn('src="https://cdn1.thr.com/sites/default/files/imagecache/768x433/2017/11/thorragnarok59e8057250eb8-h_2017.jpg"',
                           html)

    def test_create_user(self):
        """Testing if create user form displays correctly"""

        with app.test_client() as client:
            resp = client.get("/users/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>Create User</h1>", html)
            self.assertIn("First Name", html)
            self.assertIn("Last Name", html)

    def test_add_user(self):
        """Testing if user is added and shows detail page"""       

        with app.test_client() as client:
            d = {"first_name": "Scarlett", "last_name": "Johansson", "image_url": "https://cdn1-www.comingsoon.net/assets/uploads/2019/11/Black-Widow.jpg"}
            resp = client.post("/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Scarlett Johansson", html)

    def test_add_user_invalid(self):
        """Testing if correct response is given with empty inputs"""

        with app.test_client() as client:    
            d = {"first_name": "", "last_name": "", "image_url": ""}
            resp = client.post(f"/users/new", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please enter first and last name", html)        

    def test_show_edit_form(self):
        """Testing if user edit form page displays"""

        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/edit") 
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>Edit User</h1>", html)
            self.assertIn("<h5>Chris Hemsworth</h5>", html)

    def test_edit_user(self):
        """Testing if user is edited and shows detail page"""

        with app.test_client() as client:
            d = {"first_name": "Thor", "last_name": "Odinson", "image_url": "some_link"}
            resp = client.post(f"/users/{self.user_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Thor Odinson", html)

    def test_edit_user_invalid(self):
        """Testing if correct response is given with empty inputs"""

        with app.test_client() as client:    
            d = {"first_name": "", "last_name": "", "image_url": ""}
            resp = client.post(f"/users/{self.user_id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please enter first and last name", html)        

    def test_delete_user(self):
        """Testing if user is deleted and removed from list"""

        with app.test_client() as client:
            resp = client.post(f"users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Chris Hemsworth", html)