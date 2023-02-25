from datetime import datetime, timedelta
import json

from flask import Flask, make_response, current_app, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

from . import api
from ..models import db, User, Tweet
from ..tweet_validation import TweetInput
from ..utils.common import TokenGenerator, generate_response



def create_tweet(input_data):
    create_validation_schema = TweetInput()
    errors = create_validation_schema.validate(input_data)
    if errors:
        current_app.logger.info(f'[tweet] validation errors: {errors}')
        return generate_response(message=errors)

    auth_token = input_data.pop('auth_token').replace('Bearer ', '')
    token = TokenGenerator.decode_token(auth_token)
    user = User.query.filter_by(id=token.get('id')).first()
    if user is None:
        current_app.logger.info('[tweet] user is none')
        return generate_response(
            message="No record found with this email. please signup first.",
            status=400,
        )
    tweet = Tweet(user=user.id, body=input_data['body'])
    db.session.add(tweet)
    db.session.commit()

    current_app.logger.info('[tweet] finished')
    return generate_response(
        data={
            'id': tweet.id
        }, message="User login successfully", status=200
    )


@api.route('/tweet/', methods=['POST'])
def route_tweet():
    input_data = json.loads(request.data)
    # TODO: require that token is in HEADER
    auth_token = request.headers.get('Authorization')
    input_data['auth_token'] = auth_token
    response, status = create_tweet(input_data)
    return make_response(response, status)