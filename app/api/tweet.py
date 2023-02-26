from datetime import datetime, timedelta
import json

from flask import Flask, make_response, current_app, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

from . import api
from ..models import db, User, Tweet
from ..tweet_validation import TweetInput
from ..utils.common import AuthError, generate_response


def _auth_user_for_tweet(auth_token, tweet_id=None):
    '''
    if tweet_id is None, then we are just returning the user from the auth_token
    '''
    tweet = None
    user = User.get_from_bearer_token(auth_token)
    if user is None:
        current_app.logger.info('[tweet] user is none')
        raise Exception("No record found with this email. please signup first.")
    if tweet_id:
        tweet = Tweet.query.filter_by(id=tweet_id).first()
        if tweet.user != user.id:
            current_app.logger.info('[tweet] user is not the owner of this tweet')
            raise AuthError("Provided token cannot modify this tweet.")
    return user, tweet


def _validate_tweet(input_data):
    create_validation_schema = TweetInput()
    errors = create_validation_schema.validate(input_data)
    if errors:
        current_app.logger.info(f'[tweet] validation errors: {errors}')
        raise Exception(errors)

def create_tweet(input_data):
    _validate_tweet(input_data)
    user, noner = _auth_user_for_tweet(input_data.get('auth_token'))
    tweet = Tweet(user=user.id, body=input_data['body'])
    db.session.add(tweet)
    db.session.commit()

    current_app.logger.info('[tweet] finished')

    return {
        'id': tweet.id
    }, 200

def update_tweet(id, input_data):
    _validate_tweet(input_data)
    user, tweet = _auth_user_for_tweet(input_data.get('auth_token'), id)

    tweet.body = input_data.get('body')
    db.session.add(tweet)
    db.session.commit()

    current_app.logger.info('[tweet] update finished')

    return {
        'id': tweet.id
    }, 200


def delete_tweet(id, input_data):
    user, tweet = _auth_user_for_tweet(input_data.get('auth_token'), id)

    db.session.delete(tweet)
    db.session.commit()

    current_app.logger.info('[tweet] deleted')

    return {
        'id': tweet.id
    }, 200


@api.route('/tweet/', methods=['POST'], defaults={'id': None})
@api.route('/tweet/<id>/', methods=['PUT', 'DELETE'])
def route_tweet(id):
    return_data = {}
    auth_token = request.headers.get('Authorization')
    if len(request.data):
        input_data = json.loads(request.data)
    else:
        input_data = {}

    input_data['auth_token'] = auth_token

    try:
        if request.method == 'POST':
            return_data, status = create_tweet(input_data)
        elif request.method == 'PUT':
            return_data, status = update_tweet(id, input_data)
        elif request.method == 'DELETE':
            return_data, status = delete_tweet(id, input_data)
    except Exception as e:
        status = 400
        return_data = f'{e}'
        if e.__class__ == AuthError:
            status = 401
        current_app.logger.info(f'[tweet] {request.method} error: {e}')
    return make_response({'data': return_data}, status)