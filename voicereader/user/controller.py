from flask import Blueprint
from flask_pymongo import PyMongo

_user_api = Blueprint('users', __name__)
mongo = PyMongo()


def get_user_api(app):
    mongo.init_app(app)
    return _user_api


@_user_api.route('/<user_id>', methods=['GET'])
def fetch_by_id(user_id):
    pass


@_user_api.route('/', methods=['POST'])
def add():
    pass


@_user_api.route('/<user_id>/photo', methods=['POST'])
def uploadPhoto(user_id):
    pass


@_user_api.route('/<user_id>', methods=['PUT'])
def update(user_id):
    pass


@_user_api.route('/<user_id>', methods=["DELETE"])
def remove():
    pass
