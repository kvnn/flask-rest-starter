import json
import unittest

from app import create_app, db
from app.models import User, Tweet


LOGIN_USER_EMAIL = 'jane@example.com'
LOGIN_USER_PW = 'anotherpassword'

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_tweet_user_token(self):
        user = User(email=LOGIN_USER_EMAIL, password=LOGIN_USER_PW)
        db.session.add(user)
        db.session.commit()
        data = {
            "email": LOGIN_USER_EMAIL,
            "password": LOGIN_USER_PW
        }
        # login with the new account
        response = self.client.post('/api/v1/auth/login/', json=data, follow_redirects=True)
        data = json.loads(response.data)
        return data['data']['token']

    def test_tweet_lifecycle(self):
        # create
        data = {
            "body": "This is my tweet"
        }
        auth_token = self._get_tweet_user_token()
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        data['auth_token'] = auth_token
        response = self.client.post('/api/v1/tweet/', json=data, headers=headers, follow_redirects=True)
        id = json.loads(response.data)['data']['id']
        self.assertEqual(response.status_code, 200)
        tweet = Tweet.query.filter_by(id=id)[0]
        self.assertEqual(tweet.body, data['body'])

        # update
        data['body'] = 'new content'
        response = self.client.put(f'/api/v1/tweet/{id}/', json=data, headers=headers, follow_redirects=True)
        tweet = Tweet.query.filter_by(id=id)[0]
        self.assertEqual(response.status_code, 200)
        tweet = Tweet.query.filter_by(id=id)[0]
        self.assertEqual(tweet.body, data['body'])

