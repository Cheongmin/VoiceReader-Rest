from bson import ObjectId
from bson.errors import InvalidId

from voicereader.services.db import mongo
from voicereader.extensions.errors import InvalidIdError


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


def get_question_by_id(question_id):
    try:
        question_id = ObjectId(question_id)
    except InvalidId:
        raise InvalidIdError('question_id')

    pipelines = [
        {"$match": {"_id": question_id}},
        {"$addFields": {"num_of_view": {"$size": {"$ifNull": ["$read", []]}}}},
        {"$addFields": {"num_of_answers": {"$size": {"$ifNull": ["$answers", []]}}}},
        {"$project": {"answers": 0, "read": 0}}
    ]

    result = mongo.db.questions.aggregate(pipelines)
    result = list(result)

    if len(result) == 0:
        return None

    return result[0]


def get_questions_by_user_id(user_id):
    try:
        user_id = ObjectId(user_id)
    except InvalidId:
        raise InvalidIdError('user_id')

    pipelines = [
        {"$match": {"writer_id": user_id}},
        {"$addFields": {"num_of_view": {"$size": {"$ifNull": ["$read", []]}}}},
        {"$addFields": {"num_of_answers": {"$size": {"$ifNull": ["$answers", []]}}}},
        {"$project": {"answers": 0, "read": 0}}
    ]

    result = mongo.db.questions.aggregate(pipelines)
    result = list(result)

    return result
