from flask import Blueprint

question_api = Blueprint('questions', __name__)


@question_api.route('/', methods=['GET'])
def fetch_all():
    return 'Question api'


@question_api.route('/<question_id>', methods=['GET'])
def fetch_by_id(question_id):
    pass


@question_api.route('/', methods=['POST'])
def add():
    pass


@question_api.route('/<question_id>', methods=['DELETE'])
def remove(question_id):
    pass
