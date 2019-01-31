from flask_pymongo import PyMongo
from pymongo import TEXT

mongo = PyMongo()


def init_app(app):
    mongo.init_app(app)
    mongo.db.users.create_index([('fcm_uid', TEXT)], unique=True)
