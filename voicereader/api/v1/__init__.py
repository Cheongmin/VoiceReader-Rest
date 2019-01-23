from flask import Blueprint
from flask_restplus import Api

from voicereader import jwt


def create_api_v1(config):
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
    api = Api(api_v1, version='v1', title='VoiceReader API', description='This api provide data '
                                                                         'that need voicereader app')

    jwt._set_error_handler_callbacks(api)

    add_namespaces(api, config)

    return api_v1


def add_namespaces(api, config):
    from .auth.controller import api as auth_ns
    from .user.controller import api as user_ns
    from .question.controller import api as question_ns
    from .answer.controller import api as answer_ns

    if config['VOICEREADER_API_VERSION'] == 'dev version':
        add_debug_resources()

    api.add_namespace(auth_ns, path='/oauth2')
    api.add_namespace(user_ns, path='/users')
    api.add_namespace(question_ns, path='/questions')
    api.add_namespace(answer_ns, path='/questions')


def add_debug_resources():
    from .auth.controller import DebugToken
    from .auth.controller import api as auth_ns

    auth_ns.add_resource(DebugToken, '/token/debug')
