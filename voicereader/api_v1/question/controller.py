import time
import datetime
import os
import asyncio

from flask import jsonify, request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, UnsupportedMediaType
from werkzeug.datastructures import FileStorage

from bson import ObjectId
from bson.errors import InvalidId

from voicereader.services.db import mongo
from voicereader.extensions import errors
from voicereader.extensions.media import allowed_file

from .schema import question_schema, question_with_writer_schema
from ..middlewares import storage
from ..user.controller import get_user

api = Namespace('Question API', description='Question related operation')

common_parser = api.parser()
common_parser.add_argument('Authorization', location='headers', help='Bearer <access_token>')

get_parser = api.parser()
get_parser.add_argument('offset', default=0, help='skip count of questions')
get_parser.add_argument('size', default=3, help='size of questions')

post_parser = api.parser()
post_parser.add_argument('sound', type=FileStorage, location='files', required=True, help='file of sound')
post_parser.add_argument('title', type=str, location='form', required=True, help='title of question')
post_parser.add_argument('contents', type=str, location='form', required=True, help='contents of question')
post_parser.add_argument('subtitles', type=str, location='form', required=True, help='scripts of subtitle')

SOUND_PREFIX = 'sound/'
SOUND_ALLOWED_EXTENSIONS = set(['mp3', 'm4a'])


@api.route('')
@api.expect(common_parser)
class QuestionList(Resource):
    @jwt_required
    @api.doc(description='Fetch questions')
    @api.expect(get_parser)
    @api.marshal_list_with(question_with_writer_schema(api))
    @api.response(401, 'Invalid AccessToken')
    def get(self):
        args = get_parser.parse_args()

        offset = args['offset']
        size = args['size']
        result = []

        records_fetched = get_questions(offset, size)
        for record in records_fetched:
            record['writer'] = get_user(record['writer_id'])
            result.append(record)

        return result

    @jwt_required
    @api.doc(description='Add new question')
    @api.expect(post_parser)
    @api.marshal_with(question_schema(api), code=201)
    @api.response(400, 'Invalid form data')
    @api.response(401, 'Invalid AccessToken')
    @api.response(415, 'Unsupport media type only mp3, m4a')
    def post(self):
        args = post_parser.parse_args()

        json_data = dict()
        json_data['_id'] = ObjectId()
        json_data['title'] = args['title']
        json_data['subtitles'] = args['subtitles']
        json_data['contents'] = args['contents']
        json_data["writer_id"] = ObjectId(get_jwt_identity())
        json_data["created_date"] = time.mktime(datetime.datetime.utcnow().timetuple())

        sound_file = args['sound']
        extension = os.path.splitext(sound_file.filename)[1]
        sound_file.filename = str(json_data['_id']) + extension

        if not allowed_file(sound_file.filename, SOUND_ALLOWED_EXTENSIONS):
            raise UnsupportedMediaType(errors.UNSUPPORT_MEDIA_TYPE)

        json_data["sound_url"] = os.path.join(request.url, 'sound', sound_file.filename)

        storage.upload_file(SOUND_PREFIX, sound_file)

        mongo.db.questions.insert(json_data)

        return json_data, 201


@api.route('/<question_id>')
@api.expect(common_parser)
class Question(Resource):
    @jwt_required
    @api.doc(description='Fetch question by question_id')
    @api.response(200, 'Success', question_with_writer_schema(api))
    @api.response(400, 'Invalid question_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists question')
    def get(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        record = get_question_by_id(question_id)
        if record is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        record['writer'] = get_user(record['writer_id'])

        asyncio.run(add_read_to_question(question_id, ObjectId(get_jwt_identity())))

        return jsonify(record)

    @jwt_required
    @api.doc(description='Remove question by question_id')
    @api.response(204, 'Success')
    @api.response(400, 'Invalid question_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(403, 'Not equal between request user_id and writer_id')
    @api.response(404, 'Not exists question')
    def delete(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        question = get_question_by_id(question_id)
        if question is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        if str(question['writer_id']) != str(get_jwt_identity()):
            raise Forbidden(errors.NOT_EQUAL_USER_ID)

        mongo.db.questions.delete_one({"_id": question_id})

        return '', 204


def get_questions(skip, limit):
    pipelines = [
        {"$sort": {"created_date": -1}},
        {"$skip": int(skip)},
        {"$limit": int(limit)},
        {"$addFields": {"num_of_view": {"$size": {"$ifNull": ["$read", []]}}}},
        {"$addFields": {"num_of_answers": {"$size": {"$ifNull": ["$answers", []]}}}},
        {"$project": {"answers": 0, "read": 0}}
    ]

    return mongo.db.questions.aggregate(pipelines)


def get_question_by_id(obj_question_id):
    pipelines = [
        {"$match": {"_id": obj_question_id}},
        {"$addFields": {"num_of_view": {"$size": {"$ifNull": ["$read", []]}}}},
        {"$addFields": {"num_of_answers": {"$size": {"$ifNull": ["$answers", []]}}}},
        {"$project": {"answers": 0, "read": 0}}
    ]

    result = mongo.db.questions.aggregate(pipelines)
    result = list(result)

    if len(result) == 0:
        return None

    return result[0]


async def add_read_to_question(obj_question_id, obj_user_id):
    mongo.db.questions.update_one({"_id": obj_question_id}, {"$addToSet": {"read": obj_user_id}})


@api.route('/sound/<path:filename>')
@api.doc(False)
class QuestionSound(Resource):
    # @jwt_required
    def get(self, filename):
        return storage.fetch_file(SOUND_PREFIX, filename, as_attachment=True)

