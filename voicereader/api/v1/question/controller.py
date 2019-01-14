import time
import datetime
import os

from flask import jsonify, request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound, UnsupportedMediaType
from werkzeug.datastructures import FileStorage

from bson import ObjectId
from bson.errors import InvalidId

from voicereader import mongo, file_manager
from voicereader.extensions.media import allowed_file

from .schema import question_schema
from .. import errors

api = Namespace('Question API', description='Question related operation')

common_parser = api.parser()
common_parser.add_argument('Authorization', location='headers', help='Bearer <access_token>')

get_parser = api.parser()
get_parser.add_argument('offset', default=0, help='skip count of questions')
get_parser.add_argument('size', default=3, help='size of questions')

post_parser = api.parser()
post_parser.add_argument('sound', type=FileStorage, location='files', required=True, help='file of sound')
post_parser.add_argument('subtitles', type=str, location='form', required=True, help='scripts of subtitle')
post_parser.add_argument('contents', type=str, location='form', required=True, help='contents of question')

SOUND_PREFIX = 'sound/'
SOUND_ALLOWED_EXTENSIONS = set(['mp3', 'm4a'])


@api.route('')
@api.expect(common_parser)
class QuestionList(Resource):
    @jwt_required
    @api.doc(description='Fetch questions')
    @api.expect(get_parser)
    @api.marshal_list_with(question_schema(api))
    @api.response(401, 'Invalid AccessToken')
    def get(self):
        args = get_parser.parse_args()

        offset = args['offset']
        size = args['size']
        result = []

        records_fetched = mongo.db.questions.find() \
            .sort("created_date", -1).skip(int(offset)).limit(int(size))

        for record in records_fetched:
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

        file_manager.upload_file(SOUND_PREFIX, sound_file)

        mongo.db.questions.insert(json_data)

        return json_data, 201


@api.route('/<question_id>')
@api.expect(common_parser)
class Question(Resource):
    @jwt_required
    @api.doc(description='Fetch question by question_id')
    @api.response(200, 'Success', question_schema(api))
    @api.response(400, 'Invalid question_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists question')
    def get(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        records_fetched = mongo.db.questions.find_one({"_id": ObjectId(question_id)})
        if records_fetched is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        return jsonify(records_fetched)

    @jwt_required
    @api.doc(description='Remove question by question_id')
    @api.response(204, 'Success')
    @api.response(400, 'Invalid question_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists question')
    def delete(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        record_deleted = mongo.db.questions.delete_one({"$and": [{"_id": question_id},
                                                                 {"writer_id": ObjectId(get_jwt_identity())}]})

        if record_deleted.deleted_count <= 0:
            raise NotFound(errors.NOT_EXISTS_DATA)

        return '', 204


@api.route('/sound/<path:filename>')
@api.doc(False)
class QuestionSound(Resource):
    # @jwt_required
    def get(self, filename):
        return file_manager.fetch_file(SOUND_PREFIX, filename, as_attachment=True)

