import json
import ast
import datetime
import time
import os

from flask import Blueprint, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from voicereader.constant import action_result, msg_json
from voicereader.constant import MSG_NOT_FOUND_ELEMENT, MSG_NOT_CONTAIN_SOUND

_question_api = Blueprint('questions', __name__)
mongo = PyMongo()

UPLOAD_FOLDER = 'upload/sound/'
ALLOWED_EXTENSIONS = set([''])


def get_question_api(app):
    mongo.init_app(app)
    return _question_api


@_question_api.route('', methods=['GET'])
@jwt_required
def fetch_all():
    try:
        offset = request.args.get("offset", 0)
        size = request.args.get("size", 3)
        result = []

        records_fetched = mongo.db.questions.find()\
            .sort("created_date", -1).skip(int(offset)).limit(int(size))

        for record in records_fetched:
            result.append(record)

        return action_result.ok(jsonify(result))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_question_api.route('/<question_id>', methods=['GET'])
@jwt_required
def fetch_by_id(question_id):
    """ Function to fetch the questions. """
    try:
        # Fetch all the record(s)
        records_fetched = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
        if records_fetched is None:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.ok(jsonify(records_fetched))
    except Exception as ex:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return action_result.internal_server_error(msg_json(str(ex)))


@_question_api.route('/sound/<path:filename>', methods=['GET', 'POST'])
@jwt_required
def fetch_sound_file(filename):
    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename, as_attachment=True)


@_question_api.route('', methods=['POST'])
@jwt_required
def add():
    """ Function to create new question. """
    try:
        if 'sound' not in request.files:
            return action_result.bad_request(msg_json(MSG_NOT_CONTAIN_SOUND))

        # Create new question
        try:
            json_data = json.loads(request.form['json'])
            body = ast.literal_eval(json.dumps(json_data))
        except Exception as ex:
            # Bad request as request body is not available
            # Add message for debugging purpose
            return action_result.bad_request(msg_json(str(ex)))

        body['_id'] = ObjectId()
        body["writer_id"] = ObjectId(get_jwt_identity())
        body["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())

        sound_file = request.files['sound']
        extension = os.path.splitext(sound_file.filename)[1]
        file_name = str(body['_id']) + extension

        body["sound_url"] = os.path.join(request.url, 'sound', file_name)

        sound_file.save(os.path.join(UPLOAD_FOLDER, file_name))

        record_created = mongo.db.questions.insert(body)

        return action_result.created(jsonify(body))
    except Exception as ex:
        # Error while trying to create the resource
        # Add message for debugging purpose
        return action_result.internal_server_error(msg_json(str(ex)))


@_question_api.route('/<question_id>', methods=['DELETE'])
@jwt_required
def remove(question_id):
    """ Function to remove the question. """
    try:
        # Delete the question matched
        record_deleted = mongo.db.questions.delete_one({"$and": [{"_id": ObjectId(question_id)},
                                                                 {"writer_id": ObjectId(get_jwt_identity())}]})

        # Prepare the response
        if record_deleted.deleted_count > 0:
            # We return 204 No Content to imply resource updated successfully without returning
            # the deleted entity.
            return action_result.no_content()
        else:
            # Entity not found, perhaps already deleted, return 404
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))
    except Exception as ex:
        # Something went wrong server side, so return Internal Server Error.
        return action_result.internal_server_error(msg_json(str(ex)))
