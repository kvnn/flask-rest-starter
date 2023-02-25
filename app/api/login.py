from datetime import datetime
import json

import jwt
from flask import Flask, make_response, current_app, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

from . import api
from ..models import db, User
from ..user_validation import CreateLoginInputSchema
from ..utils.common import generate_response



def login_user(request, input_data):
    """
    It takes in a request and input data, validates the input data, checks if the user exists, checks if
    the password is correct, and returns a response
    :param request: The request object
    :param input_data: The data that is passed to the function
    :return: A dictionary with the keys: data, message, status
    """
    create_validation_schema = CreateLoginInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)

    get_user = User.query.filter_by(email=input_data.get("email")).first()
    if get_user is None:
        return generate_response(message="User not found", status=400)
    if get_user.check_password(input_data.get("password")):
        token = jwt.encode(
            {
                "id": get_user.id,
                "email": get_user.email,
                "username": get_user.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            current_app.config["SECRET_KEY"],
        )
        input_data["token"] = token
        return generate_response(
            data=input_data, message="User login successfully", status=200
        )
    else:
        return generate_response(
            message="Password is wrong", status=400
        )


@api.route('/auth/login/', methods=['POST'])
def route_login():
    input_data = json.loads(request.data)
    response, status = login_user(request, input_data)
    return make_response(response, status)