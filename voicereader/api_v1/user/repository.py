from bson import ObjectId
from bson.errors import InvalidId

from voicereader.services.db import mongo
from voicereader.extensions.errors import InvalidIdError


def get_user_by_id(user_id):
    try:
        user_id = ObjectId(user_id)
    except InvalidId:
        raise InvalidIdError('user_id')

    return mongo.db.users.find_one({"_id": ObjectId(user_id)})


def get_user_id_by_firebase_uid(firebase_uid):
    record = mongo.db.users.find_one({"fcm_uid": firebase_uid})
    if record is None:
        return None

    return str(record['_id'])
