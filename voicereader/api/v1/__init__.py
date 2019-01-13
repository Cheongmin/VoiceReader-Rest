from flask import Blueprint, url_for
from flask_restplus import Api

from voicereader import jwt

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api = Api(api_v1, version='v1', title='VoiceReader API', description='This api provide data '
                                                                     'that need voicereader app')

jwt._set_error_handler_callbacks(api)


def add_namespaces():
    from .auth.controller import api as auth_ns

    api.add_namespace(auth_ns, path='/oauth2')


add_namespaces()
