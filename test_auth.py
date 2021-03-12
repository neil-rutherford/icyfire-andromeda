import unittest
from app import create_app, db
from app.models import *
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False

class AuthRoutesCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register(self):
        response = self.app.test_client().post(
            '/register',
            data={
                'form-register-email': 'john@example.com',
                'form-register-password': 'password123',
                'form-register-username': 'johndoe',
                'form-register-yob': 1964,
                'form-register-gender': 1
            },
            follow_redirects=True
        )
        #self.assertEqual(response.status_code, 302)
        
        user = User.query.filter_by(email='john@example.com').first()
        #self.assertIsNotNone(user)
        self.assertEqual(user.password_hash, user.check_password('password123'))
        self.assertEqual(user.expires_on, datetime.datetime(1970,1,1))
        self.assertEqual(user.username, 'johndoe')
        self.assertIsNone(user.status)
        self.assertEqual(user.dob, datetime.datetime(1964, 1, 1))
        self.assertEqual(user.gender, 1)
        self.assertEqual(user.profile_pic, 'https://iptc.org/wp-content/uploads/2018/05/avatar-anonymous-300x300.png')
        self.assertEqual(user.coins, 0)
        self.assertFalse(user.is_verified)

if __name__ == '__main__':
    unittest.main(verbosity=2)