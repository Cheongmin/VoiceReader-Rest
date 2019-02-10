import time
import datetime

from bson import ObjectId
from bson.errors import InvalidId

from voicereader.services.db import mongo
from voicereader.extensions.errors import InvalidIdError


def create_answer(writer_id, question_id, payload):
    try:
        writer_id = ObjectId(writer_id)
    except InvalidId:
        raise InvalidIdError('writer_id')

    try:
        question_id = ObjectId(question_id)
    except InvalidId:
        raise InvalidIdError('question_id')

    payload['_id'] = ObjectId()
    payload['writer_id'] = writer_id
    payload['question_id'] = question_id
    payload['created_date'] = time.mktime(datetime.datetime.utcnow().timetuple())

    mongo.db.answers.insert_one(payload)

    return payload


def remove_answer(writer_id, answer_id):
    try:
        writer_id = ObjectId(writer_id)
    except InvalidId:
        raise InvalidIdError('writer_id')

    try:
        answer_id = ObjectId(answer_id)
    except InvalidId:
        raise InvalidIdError('answer_id')

    result = mongo.db.answers.delete_one({"_id": answer_id})

    return result.deleted_count > 0


def get_answer_by_id(question_id, answer_id):
    try:
        question_id = ObjectId(question_id)
    except InvalidId:
        raise InvalidIdError('question_id')

    try:
        answer_id = ObjectId(answer_id)
    except InvalidId:
        raise InvalidIdError('answer_id')

    answer = mongo.db.answers.find_one({'$and': [{'_id': answer_id}, {'question_id': question_id}]})

    return answer


def get_answers_by_question_id(question_id):
    try:
        question_id = ObjectId(question_id)
    except InvalidId:
        raise InvalidIdError('question_id')

    answers = mongo.db.answers.find({'question_id': question_id})

    return answers


def get_answers_by_user_id(user_id):
    try:
        user_id = ObjectId(user_id)
    except InvalidId:
        raise InvalidIdError('user_id')

    answers = mongo.db.answers.find({'writer_id': user_id})
    # print(list(answers))
    return list(answers)
