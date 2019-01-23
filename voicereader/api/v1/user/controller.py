import json
import bson
import datetime
import time
import os

from flask import request, jsonify
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Unauthorized, \
    Forbidden, NotFound, Conflict, UnsupportedMediaType
from werkzeug.datastructures import FileStorage

from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from firebase_admin import auth
from ast import literal_eval

from voicereader import mongo, file_manager
from voicereader.extensions.media import allowed_file
from .schema import post_user_schema, user_schema
from .. import errors

api = Namespace('User API', description='Users related operation')

post_parser = api.parser()
post_parser.add_argument('Authorization', location='headers', required=True, help='ID Token from firebase auth')


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
        json_data['picture'] = req_payload['picture'] if 'picture' in req_payload else ''
        json_data['_id'] = ObjectId()
        json_data['email'] = decoded_token['email']
        json_data['fcm_uid'] = decoded_token['sub']
        json_data["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())
        if json_data['picture'] == '' and 'picture' in decoded_token:
            json_data['picture'] = decoded_token['picture']

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
            return BadRequest(errors.INVALID_PAYLOAD)

        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, body)
        if record_updated.matched_count == 0:
            return NotFound(errors.NOT_EXISTS_DATA)

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


PHOTO_KEY = 'photo'
PHOTO_PREFIX = 'user-picture/'
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
            return UnsupportedMediaType(errors.UNSUPPORT_MEDIA_TYPE)

        photo_url = os.path.join(request.url, photo_file.filename)
        query = {"$set": {
            "picture": photo_url
        }}

        record_updated = mongo.db.users.update_one({"_id": ObjectId(user_id)}, query)
        if record_updated.matched_count == 0:
            return NotFound(errors.NOT_EXISTS_DATA)

        file_manager.upload_file(PHOTO_PREFIX, photo_file)

        return jsonify({
            "picture": photo_url
        })


@api.route('/<user_id>/photo/<path:file_name>')
@api.doc(False)
class UserPhotoGet(Resource):
    @jwt_required
    def get(self, user_id, file_name):
        return file_manager.fetch_file(PHOTO_PREFIX, file_name)


class DebugUser(Resource):
    @api.doc(description='Fetch all users for debug')
    @api.marshal_list_with(user_schema(api))
    def get(self):
        result = []

        for item in mongo.db.users.find():
            result.append(item)

        return result


def get_user(user_id):
    try:
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})
    except Exception as ex:
        return None


def get_user_id(firebase_uid):
    records_fetched = mongo.db.users.find_one({"fcm_uid": firebase_uid})
    if records_fetched is None:
        return None

    return str(records_fetched['_id'])
