import os

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
    version_path = current_app.config.get('VERSION_PATH', 'VERSION')

    if not os.path.exists(version_path):
        return current_app.config.get('VOICEREADER_API_DEV_VERSION', 'dev-version')

    with open(version_path) as fp:
        return fp.readline()


@blueprint.route('/api/info/env/')
@blueprint.route('/api/info/env')
def get_env():
    return current_app.config['ENV']
