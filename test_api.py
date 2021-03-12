import datetime
import unittest
from app import create_app, db
from app.models import Article, Comment, ActivityLog, Share, User, Message, ApiClient
from config import Config
import json
import redis
import uuid

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ApiRoutesCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_load_articles(self):

        politics = Article(section=1, slug='politics', timestamp=datetime.datetime.utcnow())
        world = Article(section=2, slug='world', timestamp=datetime.datetime.utcnow())
        technology = Article(section=3, slug='tech', timestamp=datetime.datetime.utcnow())
        energy = Article(section=4, slug='energy', timestamp=datetime.datetime.utcnow())
        economy = Article(section=5, slug='econ', timestamp=datetime.datetime.utcnow())
        science = Article(section=6, slug='science', timestamp=datetime.datetime.utcnow())
        health = Article(section=7, slug='health', timestamp=datetime.datetime.utcnow())
        db.session.add_all([politics, world, technology, energy, economy, science, health])
        db.session.commit()

        response = self.app.test_client().get('/_api/load/articles/all?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 7)

        response = self.app.test_client().get('/_api/load/articles/politics?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 1)

        response = self.app.test_client().get('/_api/load/articles/world?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 1)

        response = self.app.test_client().get('/_api/load/articles/technology?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 1)

        response = self.app.test_client().get('/_api/load/articles/energy?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 1)

        response = self.app.test_client().get('/_api/load/articles/economy?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 1)

        response = self.app.test_client().get('/_api/load/articles/science?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 1)

        response = self.app.test_client().get('/_api/load/articles/health?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 1)

        response = self.app.test_client().get('/_api/load/articles/blah?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_load_connections(self):
        # create four users
        u1 = User(username='john', email='john@example.com', expires_on=datetime.datetime(1970, 1, 3))
        u2 = User(username='susan', email='susan@example.com', expires_on=datetime.datetime(2030, 1, 3))
        u3 = User(username='mary', email='mary@example.com', expires_on=datetime.datetime(2001, 1, 3))
        u4 = User(username='david', email='david@example.com', expires_on=datetime.datetime(2022, 1, 3))
        db.session.add_all([u1, u2, u3, u4])

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        response = self.app.test_client().get('/_api/load/connections/type=followers&user=john?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 0)

        response = self.app.test_client().get('/_api/load/connections/type=following&user=john?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.data)
        self.assertEqual(len(response), 2)

        response = self.app.test_client().get('/_api/load/connections/type=blah&user=john?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 400)

        response = self.app.test_client().get('/_api/load/connections/type=followers&user=blah?counter=0', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_client_lookup(self):
        a = Article(
            title='example',
            description='just an example!',
            timestamp=datetime.datetime.utcnow()
        )
        
        c = ApiClient(
            consumer_key='consumer_key', 
            consumer_secret='consumer_secret',
            is_approved=False,
            is_blacklist=True,
            expires_on=datetime.datetime(2033, 1, 23),
            is_articles=False
        )
        db.session.add(c)
        db.session.add(a)
        db.session.commit()

        # Wrong consumer key
        response = self.app.test_client().post(
            '/_api/get/articles',
            data={
                'consumer_key': 'wrong_key',
                'consumer_secret': 'consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'ERROR: Authentication failed, client not found.')

        # Wrong consumer secret
        response = self.app.test_client().post(
            '/_api/get/articles',
            data={
                'consumer_key': 'consumer_key',
                'consumer_secret': 'wrong_key'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'ERROR: Authentication failed, incorrect credentials.')

        # On blacklist
        response = self.app.test_client().post(
            '/_api/get/articles',
            data={
                'consumer_key': 'consumer_key',
                'consumer_secret': 'consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'ERROR: API access has been restricted by the provider.')

        # Not approved
        c.is_blacklist = False
        db.session.commit()
        response = self.app.test_client().post(
            '/_api/get/articles',
            data={
                'consumer_key': 'consumer_key',
                'consumer_secret': 'consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'ERROR: API access has been restricted by the provider.')

        # No article permission
        c.is_approved = True
        db.session.commit()
        response = self.app.test_client().post(
            '/_api/get/articles',
            data={
                'consumer_key': 'consumer_key',
                'consumer_secret': 'consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, b'ERROR: Insufficient permissions, resource access denied.')

        # Should work
        c.is_articles = True
        db.session.commit()
        response = self.app.test_client().post(
            '/_api/get/articles',
            data={
                'consumer_key': 'consumer_key',
                'consumer_secret': 'consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

        r = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD
        )
        x = r.delete('{}'.format(c.id))
        self.assertEqual(x, 1)

    def test_rate_limits(self):
        a = Article(
            title='example',
            description='just an example!',
            timestamp=datetime.datetime.utcnow()
        )
        
        c1 = ApiClient(
            consumer_key='free_consumer_key', 
            consumer_secret='free_consumer_secret',
            is_approved=True,
            is_blacklist=False,
            expires_on=datetime.datetime(2001, 1, 23),
            is_articles=True
        )

        c2 = ApiClient(
            consumer_key='paid_member_consumer_key', 
            consumer_secret='paid_member_consumer_secret',
            is_approved=True,
            is_blacklist=False,
            expires_on=datetime.datetime(2033, 1, 23),
            is_articles=True
        )

        db.session.add_all([a, c1, c2])
        db.session.commit()

        # Test free-tier rate limits
        response = self.app.test_client().post(
                '/_api/get/articles',
                data={
                    'consumer_key': 'free_consumer_key',
                    'consumer_secret': 'free_consumer_secret'
                }
            )
        self.assertEqual(response.status_code, 200)

        counter = 0
        while counter < 61:
            response = self.app.test_client().post(
                '/_api/get/articles',
                data={
                    'consumer_key': 'free_consumer_key',
                    'consumer_secret': 'free_consumer_secret'
                }
            )
            counter += 1
        
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.data, b"ERROR: Too many requests, you are limited to 60 requests / hour.")

        r = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD
        )
        x = r.delete('{}'.format(c1.id))
        self.assertEqual(x, 1)

    def test_routes(self):
        u = User(
            email='john@example.com',
            expires_on=datetime.datetime(2022,1,1),
            username='john'
        )
        db.session.add(u)
        db.session.commit()

        c = ApiClient(
            user_id=u.id,
            consumer_key='free_consumer_key', 
            consumer_secret='free_consumer_secret',
            is_approved=True,
            is_blacklist=False,
            expires_on=datetime.datetime(2001, 1, 23),
            is_articles=True,
            is_comments=True,
            is_logs=True,
            is_shares=True,
            is_users=True,
            is_messages=True,
            is_api=True
        )
        db.session.add(c)
        db.session.commit()

        response = self.app.test_client().post(
                '/_api/post/articles',
                data={
                    'consumer_key': 'free_consumer_key',
                    'consumer_secret': 'free_consumer_secret',
                    'image_file_path': 'https://hatrabbits.com/wp-content/uploads/2017/01/random.jpg',
                    'title': 'How elephants are destroying the world',
                    'description': 'It is more insidious than you might think!',
                    'section': 4,
                    'tags': 'elephants, africa',
                    'body': "lorem ipsum!"
                }
            )
        self.assertEqual(response.status_code, 201)
        articles = Article.query.all()
        self.assertIsNotNone(articles)

        response = self.app.test_client().post(
            '/_api/get/articles',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().post(
            '/_api/get/article/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().post(
            '/_api/post/comments/{}'.format(articles[0].id),
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
                'comment': 'Great article, if I may say so myself!'
            }
        )
        self.assertEqual(response.status_code, 201)
        comments = Comment.query.all()
        self.assertIsNotNone(comments)

        response = self.app.test_client().post(
            '/_api/get/comments/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().post(
            '/_api/get/comment/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().post(
            '/_api/get/logs/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

        log = ActivityLog(
            article_id=1,
            anonymous_uuid=str(uuid.uuid4()),
            user_id=None,
            share_id=None,
            ip_address='119.244.228.229',
            referrer_page='www.facebook.com',
            user_agent='Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0',
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        response = self.app.test_client().post(
            '/_api/get/log/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['ip_address'], '119.244.228.229')

        share = Share(
            share_uuid=str(uuid.uuid4()),
            article_id=1,
            anonymous_uuid=str(uuid.uuid4()),
            ip_address='119.244.228.229',
            network=2,
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(share)
        db.session.commit()

        response = self.app.test_client().post(
            '/_api/get/shares/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().post(
            '/_api/get/share/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['ip_address'], '119.244.228.229')

        response = self.app.test_client().post(
            '/_api/post/users',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
                'email': 'susan@example.com',
                'password': 'password123',
                'username': 'suzie-q',
                'yob': 1993,
                'gender': 2
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(User.query.all()), 2)

        response = self.app.test_client().post(
            '/_api/get/users',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

        response = self.app.test_client().post(
            '/_api/get/user/2',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'suzie-q')

        response = self.app.test_client().post(
            '/_api/post/followers/2',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        john = User.query.filter_by(username='john').first()
        susan = User.query.filter_by(username='suzie-q').first()
        self.assertTrue(john.is_following(susan))

        response = self.app.test_client().post(
            '/_api/get/followers/2',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().post(
            '/_api/get/following/2',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().post(
            '/_api/get/connection/1&2',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['user1_follows_user2'])
        self.assertFalse(data['user2_follows_user1'])

        response = self.app.test_client().post(
            '/_api/post/messages',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
                'reply_to': None,
                'to_user_id': 2,
                'subject': 'Hey Susan!',
                'body': 'Hey, welcome to the platform! So happy to have you here!'
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(susan.unread_message_count(), 1)

        response = self.app.test_client().post(
            '/_api/get/messages',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

        response = self.app.test_client().post(
            '/_api/post/clients',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
                'user_id': 2,
                'is_articles': True,
                'is_comments': True,
                'is_logs': True,
                'is_shares': True,
                'is_users': True,
                'is_connections': True,
                'is_messages': True,
                'is_api': True,
                'company_name': 'Acme',
                'contact_name': 'Puthie, Edith',
                'phone_number': '(123) 456-7890',
                'email': 'edithputhie@gmail.com',
                'use_case': 'Research!',
                'developer_platform': 'Python on AWS',
                'monetization_model': 'N/A',
                'permission_justification': 'How we supposed to research without permissions!'
            }
        )
        self.assertEqual(response.status_code, 201)
        clients = ApiClient.query.all()
        self.assertIsNotNone(clients)

        response = self.app.test_client().post(
            '/_api/get/clients',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

        response = self.app.test_client().post(
            '/_api/get/client/2',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['monetization_model'], 'N/A')

        response = self.app.test_client().post(
            '/_api/post/client/2',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret',
                'is_approved': True,
                'is_blacklist': True,
                'is_articles': False,
                'is_comments': False,
                'is_logs': False,
                'is_shares': False,
                'is_users': False,
                'is_connections': False,
                'is_messages': False,
                'is_api': False
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"SUCCESS: API Client 2 updated.")

        response = self.app.test_client().post(
            '/_api/delete/comment/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 204)

        response = self.app.test_client().post(
            '/_api/delete/article/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 204)

        response = self.app.test_client().post(
            '/_api/delete/user/1',
            data={
                'consumer_key': 'free_consumer_key',
                'consumer_secret': 'free_consumer_secret'
            }
        )
        self.assertEqual(response.status_code, 204)

        r = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD
        )
        x = r.delete('{}'.format(c.id))
        self.assertEqual(x, 1)        

if __name__ == '__main__':
    unittest.main(verbosity=2)