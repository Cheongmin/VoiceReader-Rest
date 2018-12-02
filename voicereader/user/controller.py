import json
import ast
import datetime
import time
import os

from flask import Blueprint, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from voicereader.constant import action_result
from voicereader.constant import msg_json, msg_not_contain_file, msg_invalid_file, \
    MSG_NOT_EQUAL_IDENTITY, MSG_NOT_FOUND_ELEMENT
from voicereader.constant.media import allowed_file
from voicereader.tools.local_uploader import LocalUploader

from pymongo import TEXT
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from firebase_admin import auth
from binascii import Error

_user_api = Blueprint('users', __name__)
mongo = PyMongo()


PHOTO_KEY = 'photo'
PHOTO_UPLOAD_FOLDER = 'upload/user/'
PHOTO_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

file_manager = LocalUploader(PHOTO_UPLOAD_FOLDER)


def get_user_api(app):
    mongo.init_app(app)
    mongo.db.users.create_index([('fcm_uid', TEXT)], unique=True)

    file_manager.init_app(app)

    return _user_api


@_user_api.route('/<user_id>', methods=['GET'])
@jwt_required
def fetch_by_id(user_id):
    try:
        records_fetched = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        if records_fetched is None:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.ok(jsonify(records_fetched))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_user_api.route('', methods=['GET'])
def fetch_user_id_by_fcm_uid():
    fcm_uid = request.args.get('fcm_uid')

    if fcm_uid is None:
        return action_result.bad_request(msg_json('not exists fcm uid'))

    try:
        records_fetched = mongo.db.users.find_one({"fcm_uid": fcm_uid})
        if records_fetched is None:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.ok(str(records_fetched['_id']))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_user_api.route('/<user_id>/photo/<path:file_name>', methods=['GET'])
def fetch_user_photo(user_id, file_name):
    return file_manager.fetch_file(file_name)


@_user_api.route('', methods=['POST'])
def add():
    id_token = request.headers['Authorization']

    try:
        decode_token = auth.verify_id_token(id_token)

        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except Exception as ex:
            return action_result.bad_request(msg_json(str(ex)))

        body['_id'] = ObjectId()
        body['email'] = decode_token['email']
        body['fcm_uid'] = decode_token['sub']
        body["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())

        if 'picture' in decode_token:
            body['picture'] = decode_token['picture']
        else:
            body['picture'] = ''

        mongo.db.users.insert(body)

        return action_result.created(jsonify(body))
    except Error as ex:
        return action_result.unauthorized(msg_json(str(ex)))
    except ValueError as ex:
        return action_result.unauthorized(msg_json(str(ex)))
    except TypeError as ex:
        return action_result.unauthorized(msg_json(str(ex)))
    except DuplicateKeyError as ex:
        return action_result.conflict(msg_json(str(ex)))


@_user_api.route('/<user_id>/photo', methods=['POST'])
@jwt_required
def upload_photo(user_id):
    if get_jwt_identity() != user_id:
        return action_result.bad_request(msg_json(MSG_NOT_EQUAL_IDENTITY))

    try:
        if PHOTO_KEY not in request.files:
            return action_result.bad_request(msg_not_contain_file(PHOTO_KEY))

        photo_file = request.files[PHOTO_KEY]
        extension = os.path.splitext(photo_file.filename)[1]
        photo_file.filename = user_id + extension

        if not allowed_file(photo_file.filename, PHOTO_ALLOWED_EXTENSIONS):
            return action_result.unsupported_media_type(msg_invalid_file(extension))

        photo_url = os.path.join(request.url, photo_file.filename)
        query = {"$set": {
            "picture": photo_url
        }}

        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, query)
        if record_updated.matched_count == 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        file_manager.upload_file(photo_file)

        return action_result.ok(jsonify({
            "picture": photo_url
        }))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_user_api.route('/<user_id>', methods=['PUT'])
@jwt_required
def update(user_id):
    if get_jwt_identity() != user_id:
        return action_result.bad_request(msg_json(MSG_NOT_EQUAL_IDENTITY))

    try:
        try:
            body = ast.literal_eval(json.dumps({"$set": request.get_json()}))
        except Exception as ex:
            return action_result.bad_request(msg_json(str(ex)))

        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, body)
        if record_updated.matched_count == 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.ok(jsonify(body["$set"]))
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))


@_user_api.route('/<user_id>', methods=["DELETE"])
@jwt_required
def remove(user_id):
    if get_jwt_identity() != user_id:
        return action_result.bad_request(msg_json(MSG_NOT_EQUAL_IDENTITY))

    try:
        record_deleted = mongo.db.users.delete_one({"_id": ObjectId(user_id)})

        if record_deleted.deleted_count <= 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.no_content()
    except Exception as ex:
        return action_result.internal_server_error(msg_json(str(ex)))
