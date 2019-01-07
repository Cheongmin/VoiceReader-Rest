import datetime
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

jwt = JWTManager()
mongo = PyMongo()


def create_app():
    app = Flask(__name__)

    configure_app(app)
    configure_service(app)

    register_blueprints(app)
    register_server_info_handlers(app)

    return app


def configure_app(app):
    from voicereader.extensions.json_encoder import JSONEncoder

    app.config['VOICEREADER_API_VERSION'] = 'develop version'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
    if app.config['ENV'] == 'development':
        initialize_development_env(app)
    elif app.config['ENV'] == 'production':
        initialize_production_env(app)

    app.config.from_json('../config.json')
    app.config.from_json('../config.{}.json'.format(app.config['ENV']))
    app.json_encoder = JSONEncoder


def initialize_development_env(app):
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/VoiceReader'


def initialize_production_env(app):
    app.config['VOICEREADER_API_VERSION'] = os.getenv('VOICEREADER_API_VERSION')


def configure_service(app):
    jwt.init_app(app)
    mongo.init_app(app)


def register_blueprints(app):
    from voicereader.user.controller import get_user_api
    from voicereader.question.controller import get_question_api
    from voicereader.answer.controller import get_answer_api
    from voicereader.auth.controller import get_auth_api

    app.register_blueprint(get_user_api(app), url_prefix='/api/v1/users')
    app.register_blueprint(get_question_api(app), url_prefix='/api/v1/questions')
    app.register_blueprint(get_answer_api(app), url_prefix='/api/v1/questions/<question_id>/answers')
    app.register_blueprint(get_auth_api(), url_prefix='/api/v1')


def add_namespaces(api):
    from voicereader.user.controller import api as user

    api.add_namespace(user)


def register_server_info_handlers(app):
    @app.route('/api/info/version')
    def get_version():
        return 'develop version3'

    @app.route('/api/info/env')
    def get_info():
        return app.config['ENV']
