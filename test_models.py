import datetime
import unittest
from app import create_app, db
from app.models import Article, Comment, ActivityLog, Share, User, Message, ApiClient
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(email='john@example.com', username='john')
        u.set_password('correct')
        self.assertFalse(u.check_password('wrong'))
        self.assertTrue(u.check_password('correct'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_articles(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.datetime.utcnow()
        p1 = Article(slug="post from john", author=u1,
                  timestamp=now + datetime.timedelta(seconds=1))
        p2 = Article(slug="post from susan", author=u2,
                  timestamp=now + datetime.timedelta(seconds=4))
        p3 = Article(slug="post from mary", author=u3,
                  timestamp=now + datetime.timedelta(seconds=3))
        p4 = Article(slug="post from david", author=u4,
                  timestamp=now + datetime.timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_articles().all()
        f2 = u2.followed_articles().all()
        f3 = u3.followed_articles().all()
        f4 = u4.followed_articles().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

    def test_check_subscription(self):
        u1 = User(username='john', email='john@example.com', expires_on=datetime.datetime(1970,1,1))
        u2 = User(username='susan', email='susan@example.com', expires_on=datetime.datetime.utcnow() + datetime.timedelta(days=30))
        self.assertEqual(u1.check_subscription(), False)
        self.assertEqual(u2.check_subscription(), True)

    def test_unread_message_count(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        m1 = Message(to_user_id=u.id, seen_timestamp=None, body='abc')
        m2 = Message(to_user_id=u.id, seen_timestamp=datetime.datetime(1970,1,1), body='def')
        m3 = Message(to_user_id=99999, seen_timestamp=None, body='ghi')
        m4 = Message(to_user_id=u.id, seen_timestamp=None, body='jkl')
        db.session.add_all([m1, m2, m3, m4])
        db.session.commit()
        self.assertEqual(u.unread_message_count(), 2)

    def test_backrefs(self):
        u = User(username='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        c1 = Comment(user_id=u.id, comment='yeah')
        c2 = Comment(user_id=999, comment='naw')
        a1 = Article(user_id=u.id, slug='this-is-an-article')
        a2 = Article(user_id=999, slug='this-isnt')
        db.session.add_all([c1, c2, a1, a2])
        db.session.commit()
        self.assertEqual(c1.author.username, 'john')
        self.assertEqual(a1.author.email, 'john@example.com')

if __name__ == '__main__':
    unittest.main(verbosity=2)