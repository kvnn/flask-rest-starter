import json
import unittest

from app import create_app, db
from app.models import User, Tweet


LOGIN_USER_EMAIL = 'jane@example.com'
LOGIN_USER_PW = 'anotherpassword'

LOGIN_USER_EMAIL_2 = 'jackson@example.com'

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
        self.assertEqual(response.status_code, 200)
        tweet = Tweet.query.filter_by(id=id)[0]
        self.assertEqual(tweet.body, data['body'])

        # delete
        response = self.client.delete(f'/api/v1/tweet/{id}/', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        tweets = Tweet.query.filter_by(id=id)
        self.assertEqual(tweets.count(), 0)
    
    def test_tweet_auth(self):
        # create tweet for user 2
        user = User(email=LOGIN_USER_EMAIL_2, password=LOGIN_USER_PW)
        db.session.add(user)
        db.session.commit()
        orig_body = 'body'
        tweet = Tweet(user=user.id, body=orig_body)
        db.session.add(tweet)
        db.session.commit()

        # try update from user 1
        data = {
            'body':'very new body'
        }
        auth_token = self._get_tweet_user_token()
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        response = self.client.put(f'/api/v1/tweet/{tweet.id}/', json=data, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        tweet = Tweet.query.filter_by(id=tweet.id)[0]
        self.assertEqual(tweet.body, orig_body)
