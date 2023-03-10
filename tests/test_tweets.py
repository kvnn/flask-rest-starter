import json
import unittest
from urllib.parse import urlsplit, parse_qs

from app import create_app, db
from app.models import User, Tweet


LOGIN_USER_EMAIL = 'jane@example.com'
LOGIN_USER_EMAIL_2 = 'jackson@example.com'
LOGIN_USER_EMAIL_3 = 'joyce@example.com'
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

    def _create_user_get_token(self, user_data):
        user = User(email=user_data['email'], password=user_data['password'])
        db.session.add(user)
        db.session.commit()
        
        # login with the new account
        response = self.client.post('/api/v1/auth/login/', json=user_data, follow_redirects=True)
        data = json.loads(response.data)
        return user.id, data['data']['token']

    def test_tweet_lifecycle(self):
        # create
        data = {
            "body": "This is my tweet"
        }
        user_id, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL,
            "password": LOGIN_USER_PW
        })
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
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
        tweet = Tweet(user_id=user.id, body=orig_body)
        db.session.add(tweet)
        db.session.commit()

        # try update from user 1 via API
        data = {
            'body':'very new body'
        }
        user_id, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL,
            "password": LOGIN_USER_PW
        })
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        response = self.client.put(f'/api/v1/tweet/{tweet.id}/', json=data, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        tweet = Tweet.query.filter_by(id=tweet.id)[0]
        self.assertEqual(tweet.body, orig_body)
    
    def test_reply(self):
        # create original tweet
        user_id, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL,
            "password": LOGIN_USER_PW
        })
        tweet = Tweet(user_id=user_id, body='ORIGINAL TWEET BODY')
        db.session.add(tweet)
        db.session.commit()

        # create reply 1 via API
        user_id_2, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL_2,
            "password": LOGIN_USER_PW
        })
        data = {
            "body": "REPLY #1",
            "parent_id": tweet.id
        }
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        response = self.client.post('/api/v1/tweet/', json=data, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        reply_id_1 = json.loads(response.data)['data']['id']

        # create reply 2 via API
        user_id_3, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL_3,
            "password": LOGIN_USER_PW
        })
        data = {
            "body": "REPLY #2",
            "parent_id": tweet.id
        }
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        response = self.client.post('/api/v1/tweet/', json=data, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        reply_id_2 = json.loads(response.data)['data']['id']

        db.session.refresh(tweet)
        children_ids = [child.id for child in tweet.children]
        self.assertTrue(reply_id_1 in children_ids and reply_id_2 in children_ids)
    
    def test_pagination(self):
        num_tweets = 13
        # Create tweets
        user_id, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL,
            "password": LOGIN_USER_PW
        })
        for i in range(1, num_tweets+1):
            tweet = Tweet(user_id=user_id, body=f'TWEET {i} BODY')
            db.session.add(tweet)
            db.session.commit()

        tweets_per_page = self.app.config['TWEETS_PER_PAGE']
        last_page = 1 + num_tweets // tweets_per_page
        remainder = num_tweets % tweets_per_page
        query_data = {}
        path = '/api/v1/tweets/'
        for i in range(1, last_page):
            page = self.client.get(path, query_string=query_data)
            data = json.loads(page.data)
            split_url = urlsplit(data.get('next'))
            path = split_url.path
            query = split_url.query
            params = parse_qs(query)
            query_data = {k: int(v[0]) for k, v in params.items()}
            if i == last_page:
                self.assertEqual(remainder, len(data['tweets']))
            else:
                self.assertEqual(tweets_per_page, len(data['tweets']))


    def test_like_lifecycle(self):
        # Create Tweet
        user_id, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL,
            "password": LOGIN_USER_PW
        })
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        tweet = Tweet(user_id=user_id, body='ORIGINAL TWEET BODY')
        db.session.add(tweet)
        db.session.commit()

        # Create Like via API
        user_id, auth_token = self._create_user_get_token({
            "email": LOGIN_USER_EMAIL_2,
            "password": LOGIN_USER_PW
        })
        headers = {
            'Authorization': f'Bearer {auth_token}'
        }
        data = {'tweet_id': tweet.id}
        response = self.client.post(f'/api/v1/tweet/like/', json=data, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 201)

        like_id = json.loads(response.data)['data']['like_id']
        tweet = Tweet.query.filter_by(id=tweet.id)[0]
        self.assertTrue(like_id in [like.id for like in tweet.likes])

        # Delete Like via API
        data = {
            'like_id': like_id
        }
        response = self.client.delete(f'/api/v1/tweet/like/', json=data, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(like_id not in [like.id for like in tweet.likes])