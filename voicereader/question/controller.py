import json
import ast
import datetime
import time
import os

from flask import Blueprint, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId

from voicereader.constant import action_result, msg_json
from voicereader.constant import MSG_NOT_FOUND_ELEMENT, MSG_NOT_CONTAIN_SOUND, msg_invalid_file
from voicereader.constant.media import allowed_file
from voicereader.tools.s3_uploader import S3Uploader

_question_api = Blueprint('questions', __name__)
mongo = PyMongo()

SOUND_UPLOAD_FOLDER = 'upload/sound/'
SOUND_ALLOWED_EXTENSIONS = set(['mp3', 'm4a'])

file_manager = S3Uploader('sound/')


def get_question_api(app):
    mongo.init_app(app)
    file_manager.init_app(app)

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
    try:
        records_fetched = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
        if records_fetched is None:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.ok(jsonify(records_fetched))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_question_api.route('/sound/<path:filename>', methods=['GET', 'POST'])
def fetch_sound_file(filename):
    return file_manager.fetch_file(filename, as_attachment=True)


@_question_api.route('', methods=['POST'])
@jwt_required
def add():
    try:
        if 'sound' not in request.files:
            return action_result.bad_request(msg_json(MSG_NOT_CONTAIN_SOUND))

        try:
            json_data = json.loads(request.form['json'])
            body = ast.literal_eval(json.dumps(json_data))
        except Exception as ex:
            return action_result.bad_request(msg_json(str(ex)))

        body['_id'] = ObjectId()
        body["writer_id"] = ObjectId(get_jwt_identity())
        body["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())

        sound_file = request.files['sound']
        extension = os.path.splitext(sound_file.filename)[1]
        sound_file.filename = str(body['_id']) + extension

        if not allowed_file(sound_file.filename, SOUND_ALLOWED_EXTENSIONS):
            return action_result.unsupported_media_type(msg_invalid_file(extension))

        body["sound_url"] = os.path.join(request.url, 'sound', sound_file.filename)

        file_manager.upload_file(sound_file)

        mongo.db.questions.insert(body)

        return action_result.created(jsonify(body))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_question_api.route('/<question_id>', methods=['DELETE'])
@jwt_required
def remove(question_id):
    try:
        record_deleted = mongo.db.questions.delete_one({"$and": [{"_id": ObjectId(question_id)},
                                                                 {"writer_id": ObjectId(get_jwt_identity())}]})

        if record_deleted.deleted_count <= 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.no_content()
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))
