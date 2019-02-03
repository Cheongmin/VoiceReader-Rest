from flask import jsonify
from flask_jwt_extended import JWTManager


class Jwt:
    def __init__(self):
        self._jwt_manager = JWTManager()

    def init_app(self, app):
        if not app:
            raise ValueError(app)

        self._jwt_manager.init_app(app)

        error_message_key = app.config['JWT_ERROR_MESSAGE_KEY']

        @self._jwt_manager.invalid_token_loader
        def invalid_token_callback(error_string):
            return jsonify({
                error_message_key: error_string
            }), 401

    def init_api(self, api):
        self._jwt_manager._set_error_handler_callbacks(api)
