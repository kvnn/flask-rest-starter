from datetime import datetime, timedelta
import json

import jwt
from flask import Flask, make_response, current_app, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

from . import api
from ..models import db, User
from ..user_validation import LoginInput
from ..utils.common import generate_response



def login_user(request, input_data):
    """
    It takes in a request and input data, validates the input data, checks if the user exists, checks if
    the password is correct, and returns a response
    :param request: The request object
    :param input_data: The data that is passed to the function
    :return: A dictionary with the keys: data, message, status
    """
    create_validation_schema = LoginInput()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)

    get_user = User.query.filter_by(email=input_data.get("email")).first()
    if get_user is None:
        current_app.logger.info('[login] user not found')
        return {
            'message':"User not found"
        }, 400
    if get_user.verify_password(input_data.get("password")):
        current_app.logger.info('[login] creating token')
        token = jwt.encode(
            {
                "id": get_user.id,
                "email": get_user.email,
                "exp": datetime.utcnow() + timedelta(minutes=300),
            },
            current_app.config["SECRET_KEY"],
        )
        input_data["token"] = token
        return {
            'message': "Logged in",
            'token': token
        }, 200
    else:
        current_app.logger.info('[login] wrong password')
        return {
            'message': "Wrong Password"
        }, 400


@api.route('/auth/login/', methods=['POST'])
def route_login():
    input_data = json.loads(request.data)
    return_data, status = login_user(request, input_data)
    return make_response({'data': return_data}, status)