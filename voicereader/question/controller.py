from flask import Blueprint, jsonify
from flask_pymongo import PyMongo

_question_api = Blueprint('questions', __name__)
mongo = PyMongo()


def get_question_api(app):
    mongo.init_app(app)
    return _question_api


@_question_api.route('/', methods=['GET'])
def fetch_all():
    return 'Question api'


@_question_api.route('/<question_id>', methods=['GET'])
def fetch_by_id(question_id):
    doc = mongo.db.users.find({})
    return jsonify(doc)


@_question_api.route('/', methods=['POST'])
def add():
    doc = mongo.db.users.insert({'abcd': 'abcd'})
    return jsonify(doc)


@_question_api.route('/<question_id>', methods=['DELETE'])
def remove(question_id):
    pass
