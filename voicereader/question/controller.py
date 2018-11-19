import json
import ast
import datetime
import time
import os
from flask import Blueprint, request, jsonify, send_from_directory, url_for
from flask_pymongo import PyMongo
from bson import ObjectId

_question_api = Blueprint('questions', __name__)
mongo = PyMongo()

UPLOAD_FOLDER = 'upload/sound/'
ALLOWED_EXTENSIONS = set([''])


def get_question_api(app):
    mongo.init_app(app)
    return _question_api


@_question_api.route('', methods=['GET'])
def fetch_all():
    try:
        offset = request.args.get("offset", 0)
        size = request.args.get("size", 3)
        result = []

        records_fetched = mongo.db.questions.find()\
            .sort("created_date", -1).skip(int(offset)).limit(int(size))

        for record in records_fetched:
            result.append(record)

        return jsonify(result), 200
    except Exception as ex:
        print(ex)
        return "", 500


@_question_api.route('/<question_id>', methods=['GET'])
def fetch_by_id(question_id):
    """ Function to fetch the questions. """
    try:
        # Fetch all the record(s)
        records_fetched = mongo.db.questions.find_one({"_id": ObjectId(question_id)})

        if records_fetched is not None:
            return jsonify(records_fetched), 200
        else:
            return "", 404
    except Exception as ex:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        print(ex)
        return "", 500


@_question_api.route('/sound/<path:filename>', methods=['GET', 'POST'])
def fetch_sound_file(filename):
    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename, as_attachment=True)


@_question_api.route('', methods=['POST'])
def add():
    """ Function to create new question. """
    try:
        if 'sound' not in request.files:
            return "", 400

        # Create new question
        try:
            json_data = json.loads(request.form['json'])
            body = ast.literal_eval(json.dumps(json_data))
        except Exception as ex:
            # Bad request as request body is not available
            # Add message for debugging purpose
            print(ex)
            return "", 400

        body['_id'] = ObjectId()
        body["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())

        sound_file = request.files['sound']
        extension = os.path.splitext(sound_file.filename)[1]
        file_name = str(body['_id']) + extension

        body["sound_url"] = os.path.join(request.url, 'sound', file_name)

        sound_file.save(os.path.join(UPLOAD_FOLDER, file_name))

        record_created = mongo.db.questions.insert(body)

        return jsonify(body), 201
    except Exception as ex:
        # Error while trying to create the resource
        # Add message for debugging purpose
        print(ex)
        return "", 500


@_question_api.route('/<question_id>', methods=['DELETE'])
def remove(question_id):
    """ Function to remove the question. """
    try:
        # Delete the question matched
        record_deleted = mongo.db.questions.delete_one({"_id": ObjectId(question_id)})

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
