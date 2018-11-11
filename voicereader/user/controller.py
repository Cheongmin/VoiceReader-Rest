from flask import Blueprint

user_api = Blueprint('users', __name__)


@user_api.route('/<user_id>', methods=['GET'])
def fetch_by_id(user_id):
    pass


@user_api.route('/', methods=['POST'])
def add():
    pass


@user_api.route('/<user_id>/photo', methods=['POST'])
def uploadPhoto(user_id):
    pass


@user_api.route('/<user_id>', methods=['PUT'])
def update(user_id):
    pass


@user_api.route('/<user_id>', methods=["DELETE"])
def remove():
    pass
