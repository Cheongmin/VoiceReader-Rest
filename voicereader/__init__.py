import json
import datetime

from bson import ObjectId
from flask import Flask
from flask_jwt_extended import JWTManager


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_json("../config.json")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
    app.json_encoder = JSONEncoder

    initialize_extensions(app)
    initialize_dev_environment(app)
    register_blueprints(app)

    @app.route('/api/version')
    def get_version():
        return 'VoiceReader-Api version 0.1'

    @app.route('/api/info/env')
    def get_info():
        return app.config['ENV']

    return app


def initialize_extensions(app):
    jwt.init_app(app)


def initialize_dev_environment(app):
    if app.config['ENV'] != 'development':
        return

    app.config['MONGO_URI'] = 'mongodb://localhost:27017/VoiceReader'


def register_blueprints(app):
    from voicereader.user.controller import get_user_api
    from voicereader.question.controller import get_question_api
    from voicereader.answer.controller import get_answer_api
    from voicereader.auth.controller import get_auth_api

    app.register_blueprint(get_user_api(app), url_prefix='/api/v1/users')
    app.register_blueprint(get_question_api(app), url_prefix='/api/v1/questions')
    app.register_blueprint(get_answer_api(app), url_prefix='/api/v1/questions/<question_id>/answers')
    app.register_blueprint(get_auth_api(), url_prefix='/api/v1')
