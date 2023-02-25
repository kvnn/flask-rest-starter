import json
import unittest

from app import create_app, db
from app.models import User

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


    def test_register_password_too_short(self):
        # register a new account
        data = {
            "email": "john@example.com",
            "password": "cat",
            "password2": "cat"
        }
        response = self.client.post('/api/v1/auth/register/', json=data)
        self.assertEqual(response.status_code, 400)
    
    def test_register(self):
        # register a new account
        data = {
            "email": "john@example.com",
            "password": "catcat!",
            "password2": "catcat!"
        }
        response = self.client.post('/api/v1/auth/register/', json=data)
        self.assertEqual(response.status_code, 201)
    
    # def test_login(self):
    #     data = {
    #         "email": "john@example.com",
    #         "password": "catcat!"
    #     }
    #     # login with the new account
    #     response = self.client.post('/api/v1/auth/login/', json=data, follow_redirects=True)
    #     print(f'response is {response}')
    #     self.assertEqual(response.status_code, 200)
