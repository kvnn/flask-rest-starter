import json

from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy

from . import api
from ..models import db, User
from ..user_validation import CreateSignupInputSchema
from ..utils.common import generate_response


def create_user(request, input_data):
    """
    It creates a new user
    :param request: The request object
    :param input_data: This is the data that is passed to the function
    :return: A response object
    """
    create_validation_schema = CreateSignupInputSchema()
    errors = create_validation_schema.validate(input_data)
    if errors:
        return generate_response(message=errors)
    email_exists = User.query.filter_by(email=input_data.get("email")).first()
    if email_exists:
        return generate_response(
            message="Email  already taken", status=400
        )

    user = User(email=input_data['email'], password=input_data['password'])
    db.session.add(user)
    db.session.commit()
    # token = user.generate_confirmation_token()
    del input_data["password"]
    return generate_response(
        data=input_data, message="User Created", status=201
    )



@api.route('/auth/register/', methods=['POST'])
def route_register():
    input_data = json.loads(request.data)
    response, status = create_user(request, input_data)
    return make_response(response, status)
