import json
import time
import datetime

from flask import request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from bson import ObjectId
from bson.errors import InvalidId

from ast import literal_eval

from voicereader.services.db import mongo
from voicereader.extensions import errors

from .schema import answer_with_writer_schema, post_answer_schema
from ..user.controller import get_user

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

        result = []
        records_fetched = mongo.db.questions.find_one(
            {"_id": question_id})

        if records_fetched is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        if 'answers' in records_fetched:
            for record in records_fetched['answers']:
                record['writer'] = get_user(record['writer_id'])
                result.append(record)

        return result

    @jwt_required
    @api.doc(description='Add new answer', )
    @api.expect(post_answer_schema(api), validate=True)
    @api.marshal_with(answer_with_writer_schema(api), code=201)
    @api.response(400, 'Invalid question_id or request payload')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists question')
    def post(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        try:
            body = literal_eval(json.dumps(request.get_json()))
        except ValueError:
            raise BadRequest(errors.INVALID_PAYLOAD)

        body['_id'] = ObjectId()
        body['question_id'] = question_id
        body['writer_id'] = ObjectId(get_jwt_identity())
        body['created_date'] = time.mktime(datetime.datetime.utcnow().timetuple())

        records_updated = mongo.db.questions.update_one({"_id": question_id},
                                                        {"$push": {"answers": body}})

        if records_updated.modified_count <= 0:
            raise NotFound(errors.NOT_EXISTS_DATA)

        body['writer'] = get_user(ObjectId(get_jwt_identity()))

        return body, 201


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

        record = get_answer_by_id(question_id, answer_id)
        if record is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        record['writer'] = get_user(record['writer_id'])

        return record

    @jwt_required
    @api.doc(description='Remove answer by answer_id')
    @api.response(204, 'Success')
    @api.response(400, 'Invalid question_id or answer_id')
    @api.response(401, 'Invalid AccessToken')
    @api.response(404, 'Not exists answer')
    def delete(self, question_id, answer_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_QUESTION_ID)

        try:
            answer_id = ObjectId(answer_id)
        except InvalidId:
            raise BadRequest(errors.INVALID_ANSWER_ID)

        answer = get_answer_by_id(question_id, answer_id)
        if answer is None:
            raise NotFound(errors.NOT_EXISTS_DATA)

        if str(answer['writer_id']) != str(get_jwt_identity()):
            raise Forbidden(errors.NOT_EQUAL_USER_ID)

        mongo.db.questions.update_one({"_id": question_id}, {"$pull": {"answers": {"_id": answer_id}}})

        return '', 204


def get_answer_by_id(obj_question_id, obj_answer_id):
    answer = mongo.db.questions.find_one({
            "$and": [{"_id": obj_question_id}, {"answers._id": obj_answer_id}]}, {"answers.$"})

    if answer is None:
        return None

    return answer['answers'][0]
