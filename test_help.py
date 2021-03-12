import unittest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class HelpRoutesCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_help_pages(self):
        response = self.app.test_client().get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/careers', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/contact', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/change_profile_pic', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/create_account', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/delete_account', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/log_in', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/reset_password', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/set_status', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/subscribe_unsubscribe', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/subscribe_patriot', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/unsubscribe_patriot', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/account/verify_email', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/comment_article', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/follow_user', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/gift_coins', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/inbox', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/redeem_coins', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/send_message', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/unfollow_user', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/functionality/write_article', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/create_an_app', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/delete_article', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/delete_comment', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/delete_message', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/delete_user', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_article', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_articles', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_client', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_clients', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_comment', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_comments', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_connection', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_followers', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_following', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_log', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_logs', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_message', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_messages', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_share', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_shares', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_user', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/get_users', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/post_articles', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/post_client', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/post_clients', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/post_comments', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/post_followers', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/post_messages', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/post_users', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/subscribe_to_premium_api', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/help/api/unsubscribe_from_premium_api', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_legal_pages(self):
        response = self.app.test_client().get('/legal/privacy-policy', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/legal/terms-of-service', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/legal/cookies', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/legal/disclaimers', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/legal/api-terms-of-use', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.app.test_client().get('/legal/content-policy', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main(verbosity=2)