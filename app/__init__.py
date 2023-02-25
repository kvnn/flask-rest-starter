from flask import Flask, request, jsonify, session

from config import config
from .api import api as api_blueprint
from .models import db


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app

