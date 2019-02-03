from flask import Blueprint
from flask_restplus import Api

from .auth.controller import api as auth_namespace
from .user.controller import api as user_namespace
from .question.controller import api as question_namespace
from .answer.controller import api as answer_namespace

from .middlewares import jwt

blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api = Api(blueprint, version='v1', title='VoiceReader API',
          description='This api provide data that need voicereader app')

api.add_namespace(auth_namespace, path='/oauth2')
api.add_namespace(user_namespace, path='/users')
api.add_namespace(question_namespace, path='/questions')
api.add_namespace(answer_namespace, path='/questions')

jwt.init_app(api)
