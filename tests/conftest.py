import pytest

from voicereader import application
from flask import Flask


@pytest.fixture(scope='module')
def app():
    app = application.create()
    app.config['TESTING'] = True

    app_context = app.app_context()
    app_context.push()

    yield app

    app_context.pop()


@pytest.fixture(scope='module')
def app_client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def flask_app():
    flask = Flask(__name__)
    flask.config['TESTING'] = True
    flask.config['ENV'] = 'testing'
    flask.config['VOICEREADER_API_DEV_VERSION'] = 'testing version'

    return flask


@pytest.fixture(scope='function')
def flask_client(flask_app):
    return flask_app.test_client()
