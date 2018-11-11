from flask import Blueprint

question_api = Blueprint('questions', __name__)


@question_api.route('/')
def index():
    return 'Question api'
