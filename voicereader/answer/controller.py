from flask import Blueprint, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

_answer_api = Blueprint('answers', __name__)
mongo = PyMongo()


def get_answer_api(app):
    mongo.init_app(app)
    return _answer_api


@_answer_api.route('', methods=['GET'])
def fetch_all(question_id):
    return "answer api"


@_answer_api.route('/<answer_id>', methods=['GET'])
def fetch_by_id(question_id, answer_id):
    pass


@_answer_api.route('', methods=['POST'])
def add(question_id):
    pass


@_answer_api.route('/<answer_id>', methods=['DELETE'])
def remove(question_id, answer_id):
    pass
