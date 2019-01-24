from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

from .services.s3_uploader import S3Uploader

jwt = JWTManager()
mongo = PyMongo()
file_manager = S3Uploader()


def create_app():
    app = Flask(__name__)

    configure_app(app)
    configure_service(app)

    register_blueprints(app)
    register_server_info_handlers(app)

    return app


def configure_app(app):
    from voicereader.extensions.json_encoder import JSONEncoder

    app.config.from_json('../config.json')
    app.config.from_json('../config.{}.json'.format(app.config['ENV']), True)
    app.config.from_envvar('MONGO_URI', True)
    app.config.from_envvar('VOICEREADER_API_VERSION', True)

    app.json_encoder = JSONEncoder


def configure_service(app):
    file_manager.init_app(app)

    from pymongo import TEXT

    mongo.init_app(app)
    mongo.db.users.create_index([('fcm_uid', TEXT)], unique=True)

    jwt.init_app(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            'message': error_string
        }), 401


def register_blueprints(app):
    from .api.v1 import api_v1

    app.register_blueprint(api_v1)


def register_server_info_handlers(app):
    @app.route('/api/info/version')
    def get_version():
        return app.config['VOICEREADER_API_VERSION']

    @app.route('/api/info/env')
    def get_info():
        return app.config['ENV']
