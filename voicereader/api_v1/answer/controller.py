import json

from flask import request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from bson import ObjectId
from bson.errors import InvalidId

from ast import literal_eval

from voicereader.services.db import mongo
from voicereader.extensions import errors

from . import repository as answer_repository
from .schema import answer_with_writer_schema, post_answer_schema
from ..user import repository as user_repository
from ..question import repository as question_repository

from voicereader.extensions.errors import InvalidIdError, NotExistsDataError

api = Namespace('Answer about Question API', description='Answers related operation')

common_parser = api.parser()
common_parser.add_argument('Authorization', location='headers', required=True, help='Bearer <access_token>')


@api.route('/<question_id>/answers')
@api.expect(common_parser)
class AnswerList(Resource):
    @jwt_required
    @api.doc(description='Fetch answers by question_id')
    @api.marshal_list_with(answer_with_writer_schema(api))
    @api.response(400, 'Invalid question_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists question')
    def get(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        records_fetched = mongo.db.questions.find_one(
            {"_id": question_id})

        if records_fetched is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        result = []
        if 'answers' in records_fetched:
            for answer_id in records_fetched['answers']:
                answer = answer_repository.get_answer_by_id(question_id, answer_id)
                answer['writer'] = user_repository.get_user_by_id(answer['writer_id'])

                result.append(answer)

        return result

    @jwt_required
    @api.doc(description='Add new answer')
    @api.expect(post_answer_schema(api), validate=True)
    @api.marshal_with(answer_with_writer_schema(api), code=201)
    @api.response(400, 'Invalid question_id or request payload')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists question')
    def post(self, question_id):
        try:
            body = literal_eval(json.dumps(request.get_json()))
        except ValueError:
            raise BadRequest(errors.INVALID_PAYLOAD)

        try:
            result = answer_repository.create_answer(get_jwt_identity(), question_id, body)
        except InvalidIdError as ex:
            raise BadRequest(ex)

        try:
            question_repository.add_answer_reference(question_id, result['_id'])
        except NotExistsDataError as ex:
            raise NotFound(ex)

        result['writer'] = user_repository.get_user_by_id(get_jwt_identity())

        return result, 201


@api.route('/<question_id>/answers/<answer_id>')
@api.expect(common_parser)
class Answer(Resource):
    @jwt_required
    @api.doc(description='Fetch answer by answer_id')
    @api.marshal_with(answer_with_writer_schema(api))
    @api.response(400, 'Invalid question_id or answer_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists answer')
    def get(self, question_id, answer_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        try:
            answer_id = ObjectId(answer_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_ANSWER_ID)

        record = answer_repository.get_answer_by_id(question_id, answer_id)
        if record is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        record['writer'] = user_repository.get_user_by_id(record['writer_id'])

        return record

    @jwt_required
    @api.doc(description='Remove answer by answer_id')
    @api.response(204, 'Success')
    @api.response(400, 'Invalid question_id or answer_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists answer')
    def delete(self, question_id, answer_id):
        # question_id Validation 필요
        deleted = answer_repository.remove_answer(get_jwt_identity(), answer_id)
        if not deleted:
            raise NotFound(errors.NOT_EXISTS_DATA)

        # 추가 구현 필요
        # if str(answer['writer_id']) != str(get_jwt_identity()):
        #     raise Forbidden(errors.NOT_EQUAL_USER_ID)

        question_repository.remove_answer_reference(question_id, answer_id)

        return '', 204
