from logging.config import dictConfig
import os

from flask import Flask, request, jsonify, session
from dotenv import load_dotenv

from config import config
from .api import api as api_blueprint
from .models import db

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    if config_name in ['default', 'development', 'testing']:
        with app.app_context():
            db.create_all()

    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app

