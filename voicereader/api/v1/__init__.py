from flask import Blueprint, url_for
from flask_restplus import Api

from voicereader import jwt

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api = Api(api_v1, version='v1', title='VoiceReader API', description='This api provide data '
                                                                     'that need voicereader app')

jwt._set_error_handler_callbacks(api)


def add_namespaces():
    from .auth.controller import api as auth_ns
    from .user.controller import api as user_ns
    from .question.controller import api as question_ns

    api.add_namespace(auth_ns, path='/oauth2')
    api.add_namespace(user_ns, path='/users')
    api.add_namespace(question_ns, path='/questions')


add_namespaces()
