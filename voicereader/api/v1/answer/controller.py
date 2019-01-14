import json
import time
import datetime

from flask import request
from flask_restplus import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound

from bson import ObjectId
from bson.errors import InvalidId

from ast import literal_eval

from voicereader import mongo

from .schema import answer_schema

api = Namespace('Answer about Question API', description='Answers related operation')

common_parser = api.parser()
common_parser.add_argument('Authorization', location='headers', required=True, help='Bearer <access_token>')


@api.route('/<question_id>/answers')
@api.expect(common_parser)
class AnswerList(Resource):
    @api.doc(description='Request fetch answers by QuestionId')
    @api.marshal_list_with(answer_schema(api))
    @api.response(400, 'Invalid question id')
    @api.response(401, 'Unauthorized access_token')
    @api.response(404, 'Not exists question')
    def get(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest('Invalid question id')

        result = []
        records_fetched = mongo.db.questions.find_one(
            {"_id": question_id})

        if records_fetched is None:
            raise NotFound('Not exists question')

        if 'answers' in records_fetched:
            for record in records_fetched['answers']:
                result.append(record)

        return result

    @api.doc(description='Request add new answer')
    @api.marshal_with(answer_schema(api), code=201)
    @api.response(400, 'Invalid question_id or request payload')
    @api.response(401, 'Unauthorized access_token')
    @api.response(404, 'Not exists question')
    def post(self, question_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest('Invalid question id')

        try:
            body = literal_eval(json.dumps(request.get_json()))
        except ValueError:
            raise BadRequest('Invalid answer')

        body['_id'] = ObjectId()
        body['question_id'] = question_id
        body['writer_id'] = ObjectId(get_jwt_identity())
        body['created_date'] = time.mktime(datetime.datetime.utcnow().timetuple())

        records_updated = mongo.db.questions.update_one({"_id": question_id},
                                                        {"$push": {"answers": body}})

        if records_updated.modified_count <= 0:
            raise NotFound('Not exists question')

        return body, 201


@api.route('/<question_id>/<answer_id>')
@api.expect(common_parser)
class Answer(Resource):
    @jwt_required
    @api.doc(description='Request fetch answer by AnswerId')
    @api.marshal_with(answer_schema(api))
    @api.response(400, 'Invalid QuestionId or AnswerId')
    @api.response(401, 'Unauthorized AccessToken')
    @api.response(404, 'Not exists answer')
    def get(self, question_id, answer_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest('Invalid QuestionId')

        try:
            answer_id = ObjectId(answer_id)
        except InvalidId:
            raise BadRequest('Invalid AnswerId')

        records_fetched = mongo.db.questions.find_one({
            "$and": [{"_id": question_id},
                     {"answers._id": answer_id}]}, {"answers.$"})

        if records_fetched is None:
            raise NotFound('Not exists answer')

        return records_fetched['answers'][0]

    @api.doc(description='Remove answer by AnswerId')
    @api.response(204, 'Success')
    @api.response(400, 'Invalid QuestionId or AnswerId')
    @api.response(401, 'Unauthorized AccessToken')
    @api.response(404, 'Not exists answer')
    def delete(self, question_id, answer_id):
        try:
            question_id = ObjectId(question_id)
        except InvalidId:
            raise BadRequest('Invalid QuestionId')

        try:
            answer_id = ObjectId(answer_id)
        except InvalidId:
            raise BadRequest('Invalid AnswerId')

        query = {"$and": [{"_id": answer_id}, {"writer_id": ObjectId(get_jwt_identity())}]}

        records_updated = mongo.db.questions.update_one({"_id": question_id},
                                                        {"$pull": {"answers": query}})

        if records_updated.modified_count <= 0:
            raise NotFound('Not exists answer')

        return '', 204
