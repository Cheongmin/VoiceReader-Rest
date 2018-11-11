from flask import Blueprint

user_api = Blueprint('users', __name__)


@user_api.route('/')
def index():
    return 'Users Api'
