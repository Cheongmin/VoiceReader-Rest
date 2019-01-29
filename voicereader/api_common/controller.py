from flask import Blueprint, current_app, redirect

blueprint = Blueprint('api_common', __name__)


@blueprint.route('/')
def home():
    return redirect('/api/v1/')


@blueprint.route('/api/ping/')
@blueprint.route('/api/ping')
def ping():
    return 'pong'


@blueprint.route('/api/info/version/')
@blueprint.route('/api/info/version')
def get_version():
    return current_app.config['VOICEREADER_API_VERSION']


@blueprint.route('/api/info/env/')
@blueprint.route('/api/info/env')
def get_env():
    return current_app.config['ENV']
