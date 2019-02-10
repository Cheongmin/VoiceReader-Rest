import json
import bson
import datetime
import time
import os

from flask import request, jsonify, make_response
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Unauthorized, \
    Forbidden, NotFound, Conflict, UnsupportedMediaType
from werkzeug.datastructures import FileStorage

from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from firebase_admin import auth
from ast import literal_eval

from . import repository as user_repository
from .schema import post_user_schema, user_schema
from ..middlewares import storage
from ..answer.schema import answer_schema
from ..question.schema import question_schema
from ..question import repository as question_repository

from voicereader.services.db import mongo
from voicereader.extensions import errors
from voicereader.extensions.media import allowed_file

api = Namespace('User API', description='Users related operation')

post_parser = api.parser()
post_parser.add_argument('Authorization', location='headers', required=True, help='ID Token from firebase auth')


DEFAULT_USER_PHOTO_PATH = '/00/photo/default_user_profile.png'


@api.route('')
class UserList(Resource):
    @api.doc(description='Add new user', parser=post_parser, body=post_user_schema(api), validate=True)
    @api.marshal_with(user_schema(api), code=201)
    @api.response(400, 'Invalid user schema')
    @api.response(401, 'Invalid IdToken')
    @api.response(409, 'Already exists user')
    def post(self):
        args = parser.parse_args()

        id_token = args['Authorization']

        try:
            decoded_token = auth.verify_id_token(id_token)
        except ValueError:
            raise Unauthorized(errors.INVALID_ID_TOKEN)

        if not request.is_json:
            raise BadRequest(errors.INVALID_PAYLOAD)

        req_payload = request.get_json()

        json_data = dict()
        json_data['display_name'] = req_payload['display_name']
        json_data['_id'] = ObjectId()
        json_data['email'] = decoded_token['email']
        json_data['fcm_uid'] = decoded_token['sub']
        json_data["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())
        if 'picture' in req_payload:
            json_data['picture'] = req_payload['picture']
        else:
            json_data['picture'] = request.base_url + DEFAULT_USER_PHOTO_PATH

        try:
            mongo.db.users.insert(json_data)
        except DuplicateKeyError:
            raise Conflict(errors.ALREADY_EXISTS_USER)

        return json_data, 201


parser = api.parser()
parser.add_argument('Authorization', location='headers', required=True, help='Bearer <access_token>')


@api.route('/<user_id>')
@api.param('user_id', description='User ID')
@api.expect(parser)
class User(Resource):
    @jwt_required
    @api.doc(description='Fetch user by user_id')
    @api.response(200, 'Success', user_schema(api))
    @api.response(400, 'Invalid user_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists user')
    def get(self, user_id):
        try:
            user_id = ObjectId(user_id)
        except bson.errors.InvalidId:
            raise BadRequest(errors.INVALID_USER_ID)

        record_fetched = mongo.db.users.find_one({"_id": user_id})
        if record_fetched is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        return jsonify(record_fetched)

    @jwt_required
    @api.doc(description='Update user by user_id', body=user_schema(api), validate=True)
    @api.response(200, 'Success', user_schema(api))
    @api.response(400, 'Invalid user schema')
    @api.response(401, 'Invalid AccessToken')
    @api.response(403, 'Not equal user id that included token and request user id')
    @api.response(404, 'Not exists user')
    def put(self, user_id):
        if get_jwt_identity() != user_id:
            raise Forbidden()

        try:
            body = literal_eval(json.dumps({"$set": request.get_json()}))
        except ValueError:
            raise BadRequest(errors.INVALID_PAYLOAD)

        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, body)
        if record_updated.matched_count == 0:
            raise NotFound(errors.NOT_EXISTS_DATA)

        return jsonify(body['$set'])

    @jwt_required
    @api.doc(description='Remove user by user_id')
    @api.response(204, 'Success')
    @api.response(403, 'Not equal User ID that included token and request user_id')
    @api.response(404, 'Not exists user')
    def delete(self, user_id):
        if get_jwt_identity() != user_id:
            raise Forbidden()

        record_deleted = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        if record_deleted.deleted_count < 1:
            raise NotFound(errors.NOT_EXISTS_DATA)

        return '', 204


@api.route('/<user_id>/questions')
@api.param('user_id', description='User ID')
@api.expect(parser)
class UserQuestions(Resource):
    @jwt_required
    @api.doc(description='Fetch questions written by user_id')
    @api.marshal_list_with(question_schema(api))
    @api.response(403, 'Not equal User ID that included token and request user_id')
    def get(self, user_id):
        if get_jwt_identity() != user_id:
            raise Forbidden()

        user = user_repository.get_user_by_id(user_id)
        if user is None:
            raise Forbidden(errors.NOT_EXISTS_DATA)

        result = question_repository.get_questions_by_user_id(user_id)

        return result


@api.route('/<user_id>/answers')
@api.param('user_id', description='User ID')
@api.expect(parser)
class UserAnswers(Resource):
    @jwt_required
    @api.doc(description='Fetch answers written by user_id')
    @api.marshal_list_with(answer_schema(api))
    def get(self, user_id):
        pass


PHOTO_KEY = 'photo'
PHOTO_RESOURCE = 'user-picture'
PHOTO_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

post_photo_parser = api.parser()
post_photo_parser.add_argument(PHOTO_KEY, type=FileStorage, location='files', required=True, help='Photo of user')


@api.route('/<user_id>/photo')
@api.param('user_id', description='User ID')
@api.expect(parser)
class UserPhoto(Resource):
    @jwt_required
    @api.doc(description='Upload user photo')
    @api.expect(post_photo_parser)
    @api.response(200, 'Success')
    @api.response(403, 'Not equal user id that included token and request user id')
    @api.response(404, 'Not exists user')
    @api.response(415, "Only allowed media type [png, jpg, jpeg]")
    def post(self, user_id):
        if get_jwt_identity() != user_id:
            raise Forbidden()

        args = post_photo_parser.parse_args()
        photo_file = args[PHOTO_KEY]
        extension = os.path.splitext(photo_file.filename)[1]
        photo_file.filename = user_id + extension

        if not allowed_file(photo_file.filename, PHOTO_ALLOWED_EXTENSIONS):
            raise UnsupportedMediaType(errors.UNSUPPORT_MEDIA_TYPE)

        photo_url = os.path.join(request.url, photo_file.filename)
        query = {"$set": {
            "picture": photo_url
        }}

        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, query)
        if record_updated.matched_count == 0:
            raise NotFound(errors.NOT_EXISTS_DATA)

        storage.upload_file(PHOTO_RESOURCE, photo_file)

        return jsonify({
            "picture": photo_url
        })


@api.route('/<user_id>/photo/<path:file_name>')
@api.doc(False)
class UserPhotoGet(Resource):
    def get(self, user_id, file_name):
        file = storage.fetch_file(PHOTO_RESOURCE, file_name)
        if not file:
            raise NotFound()

        response = make_response(file)
        response.headers['Content-Type'] = 'image'
        response.status_code = 200

        return response


@api.route('/debug')
class DebugUser(Resource):
    @api.doc(description='Fetch all users for debug')
    @api.marshal_list_with(user_schema(api))
    def get(self):
        result = []

        for item in mongo.db.users.find():
            result.append(item)

        return result

