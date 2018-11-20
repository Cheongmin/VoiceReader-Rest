import json
import ast
import datetime
import time
from flask import Blueprint, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from firebase_admin import auth
from binascii import Error

_user_api = Blueprint('users', __name__)
mongo = PyMongo()


def get_user_api(app):
    mongo.init_app(app)
    return _user_api


@_user_api.route('/<user_id>', methods=['GET'])
def fetch_by_id(user_id):
    """ Function to fetch the users. """
    try:
        # Fetch all the record(s)
        records_fetched = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        if records_fetched is not None:
            return jsonify(records_fetched), 200
        else:
            return "", 404
    except Exception as ex:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        print(ex)
        return "", 500


@_user_api.route('', methods=['GET'])
def fetch_user_id_by_fcm_uid():
    fcm_uid = request.args.get('fcm_uid')

    if fcm_uid is None:
        return '', 400

    try:
        records_fetched = mongo.db.users.find_one({"fcm_uid": fcm_uid})

        if records_fetched is not None:
            return str(records_fetched['_id'])
        else:
            return '', 404
    except Exception as ex:
        print(ex)
        return '', 500


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
            return ex, 400

        body['_id'] = ObjectId()
        body['email'] = decode_token['email']
        body['fcm_uid'] = decode_token['sub']
        body["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())

        mongo.db.users.insert(body)

        return jsonify(body), 201
    except Error as ex:
        return str(ex), 401
    except ValueError as ex:
        return str(ex), 401
    except Exception as ex:
        # Error while trying to create the resource
        # Add message for debugging purpose
        return str(ex), 500


@_user_api.route('/<user_id>/photo', methods=['POST'])
def upload_photo(user_id):
    pass


@_user_api.route('/<user_id>', methods=['PUT'])
def update(user_id):
    """ Function to update the user. """
    try:
        # Get the value which needs to be updated
        try:
            body = ast.literal_eval(json.dumps({"$set": request.get_json()}))
        except Exception as ex:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            print(ex)
            return "", 400

        # Updating the user
        records_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, body)

        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return "", 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return "", 404
    except Exception as ex:
        # Error while trying to update the resource
        # Add message for debugging purpose
        print(ex)
        return "", 500


@_user_api.route('/<user_id>', methods=["DELETE"])
def remove(user_id):
    """ Function to remove the user. """
    try:
        # Delete the user matched
        record_deleted = mongo.db.users.delete_one({"_id": ObjectId(user_id)})

        # Prepare the response
        if record_deleted.deleted_count > 0:
            # We return 204 No Content to imply resource updated successfully without returning
            # the deleted entity.
            return "", 204
        else:
            # Entity not found, perhaps already deleted, return 404
            return "", 404
    except Exception as ex:
        # Something went wrong server side, so return Internal Server Error.
        print(ex)
        return "", 500
