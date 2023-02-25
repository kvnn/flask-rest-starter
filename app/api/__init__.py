from flask import Blueprint

api = Blueprint('api', __name__)

print(f'name is {__name__}')

from . import register, login, tweet