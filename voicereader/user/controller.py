import json
import ast
import datetime
import time
import os

from flask import Blueprint, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from voicereader.constant import action_result
from voicereader.constant import msg_json, msg_not_contain_file, \
    MSG_NOT_EQUAL_IDENTITY, MSG_NOT_FOUND_ELEMENT

from pymongo import TEXT
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from firebase_admin import auth
from binascii import Error

_user_api = Blueprint('users', __name__)
mongo = PyMongo()


PHOTO_KEY = 'photo'
PHOTO_UPLOAD_FOLDER = 'upload/user/'


def get_user_api(app):
    mongo.init_app(app)
    mongo.db.users.create_index([('fcm_uid', TEXT)], unique=True)

    if not os.path.exists(PHOTO_UPLOAD_FOLDER):
        os.makedirs(PHOTO_UPLOAD_FOLDER)

    return _user_api


@_user_api.route('/<user_id>', methods=['GET'])
@jwt_required
def fetch_by_id(user_id):
    """ Function to fetch the users. """
    try:
        # Fetch all the record(s)
        records_fetched = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        if records_fetched is not None:
            return action_result.ok(jsonify(records_fetched))
        else:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))
    except Exception as ex:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
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
    return send_from_directory(os.path.abspath(PHOTO_UPLOAD_FOLDER), file_name, as_attachment=True)


@_user_api.route('', methods=['POST'])
def add():
    """ Function to create new user. """
    id_token = request.headers['Authorization']

    try:
        decode_token = auth.verify_id_token(id_token)
        # Create new user
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except Exception as ex:
            # Bad request as request body is not available
            # Add message for debugging purpose
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
        file_name = user_id + extension

        photo_file.save(os.path.join(PHOTO_UPLOAD_FOLDER, file_name))

        photo_url = os.path.join(request.url, file_name)
        query = {"$set": {
            "picture": photo_url
        }}

        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, query)
        if record_updated.matched_count == 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.ok(jsonify({
            "picture": photo_url
        }))
    except Exception as ex:
        # Error while trying to create the resource
        # Add message for debugging purpose
        return action_result.internal_server_error(msg_json(str(ex)))


@_user_api.route('/<user_id>', methods=['PUT'])
@jwt_required
def update(user_id):
    """ Function to update the user. """
    if get_jwt_identity() != user_id:
        return action_result.bad_request(msg_json(MSG_NOT_EQUAL_IDENTITY))

    try:
        # Get the value which needs to be updated
        try:
            body = ast.literal_eval(json.dumps({"$set": request.get_json()}))
        except Exception as ex:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            return action_result.bad_request(msg_json(str(ex)))

        # Updating the user
        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, body)
        if record_updated.matched_count == 0:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))

        return action_result.ok(jsonify(body["$set"]))
    except Exception as ex:
        # Error while trying to update the resource
        # Add message for debugging purpose
        return action_result.internal_server_error(msg_json(str(ex)))


@_user_api.route('/<user_id>', methods=["DELETE"])
@jwt_required
def remove(user_id):
    """ Function to remove the user. """
    if get_jwt_identity() != user_id:
        return action_result.bad_request(msg_json(MSG_NOT_EQUAL_IDENTITY))

    try:
        # Delete the user matched
        record_deleted = mongo.db.users.delete_one({"_id": ObjectId(user_id)})

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
