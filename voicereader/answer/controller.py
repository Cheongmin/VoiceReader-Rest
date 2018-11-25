import json
import time
import datetime
import ast

from flask import Blueprint, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from voicereader.constant import action_result, msg_json
from voicereader.constant import MSG_NOT_FOUND_ELEMENT

_answer_api = Blueprint('answers', __name__)
mongo = PyMongo()


def get_answer_api(app):
    mongo.init_app(app)
    return _answer_api


@_answer_api.route('', methods=['GET'])
@jwt_required
def fetch_all(question_id):
    try:
        result = []

        records_fetched = mongo.db.questions.find_one(
            {"_id": ObjectId(question_id)})

        if records_fetched is None:
            return action_result.not_found(MSG_NOT_FOUND_ELEMENT)

        if 'answers' in records_fetched:
            for record in records_fetched['answers']:
                result.append(record)

        return action_result.ok(jsonify(result))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_answer_api.route('/<answer_id>', methods=['GET'])
@jwt_required
def fetch_by_id(question_id, answer_id):
    try:
        records_fetched = mongo.db.questions.find_one({
            "$and": [{"_id": ObjectId(question_id)},
                     {"answers._id": ObjectId(answer_id)}]}, {"answers.$"})

        if records_fetched is None:
            return action_result.not_found(MSG_NOT_FOUND_ELEMENT)

        return action_result.ok(jsonify(records_fetched['answers'][0]))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_answer_api.route('', methods=['POST'])
@jwt_required
def add(question_id):
    try:
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except Exception as ex:
            return action_result.bad_request(msg_json(str(ex)))

        body['_id'] = ObjectId()
        body['question_id'] = ObjectId(question_id)
        body['writer_id'] = ObjectId(get_jwt_identity())
        body['created_date'] = time.mktime(datetime.datetime.utcnow().timetuple())

        records_updated = mongo.db.questions.update_one({"_id": ObjectId(question_id)},
                                                        {"$push": {"answers": body}})

        if records_updated.modified_count <= 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.created(jsonify(body))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_answer_api.route('/<answer_id>', methods=['DELETE'])
@jwt_required
def remove(question_id, answer_id):
    try:
        query = {"$and": [{"_id": ObjectId(answer_id)}, {"writer_id": ObjectId(get_jwt_identity())}]}

        records_updated = mongo.db.questions.update_one({"_id": ObjectId(question_id)},
                                                        {"$pull": {"answers": query}})

        if records_updated.modified_count <= 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.no_content()
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))
