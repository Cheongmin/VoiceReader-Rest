import json
import time
import datetime
import ast

from flask import Blueprint, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from voicereader.constant import action_result

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
            return "", 404

        if 'answers' in records_fetched:
            for record in records_fetched['answers']:
                result.append(record)

        return jsonify(result), 200
    except Exception as ex:
        print(ex)
        return "", 500


@_answer_api.route('/<answer_id>', methods=['GET'])
@jwt_required
def fetch_by_id(question_id, answer_id):
    """ Function to fetch the answer by id. """
    try:
        # Fetch all the record(s)
        records_fetched = mongo.db.questions.find_one({
            "$and": [{"_id": ObjectId(question_id)},
                     {"answers._id": ObjectId(answer_id)}]}, {"answers.$"})

        if records_fetched is not None:
            return jsonify(records_fetched['answers'][0]), 200
        else:
            return "", 404
    except Exception as ex:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        print(ex)
        return "", 500


@_answer_api.route('', methods=['POST'])
@jwt_required
def add(question_id):
    try:
        # Create new user
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except Exception as ex:
            # Bad request as request body is not available
            # Add message for debugging purpose
            return ex, 400

        body['_id'] = ObjectId()
        body['question_id'] = ObjectId(question_id)
        body['writer_id'] = ObjectId(get_jwt_identity())
        body['created_date'] = time.mktime(datetime.datetime.utcnow().timetuple())

        records_updated = mongo.db.questions.update_one({"_id": ObjectId(question_id)},
                                                        {"$push": {"answers": body}})

        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return jsonify(body), 201
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return "", 404
    except Exception as ex:
        # Error while trying to create the resource
        # Add message for debugging purpose
        print(ex)
        return "", 500


@_answer_api.route('/<answer_id>', methods=['DELETE'])
@jwt_required
def remove(question_id, answer_id):
    try:
        query = {"$and": [{"_id": ObjectId(answer_id)}, {"writer_id": ObjectId(get_jwt_identity())}]}

        # Delete the user matched
        records_updated = mongo.db.questions.update_one({"_id": ObjectId(question_id)},
                                                        {"$pull": {"answers": query}})

        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return answer_id, 204
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return "", 404
    except Exception as ex:
        # Something went wrong server side, so return Internal Server Error.
        print(ex)
        return "", 500
