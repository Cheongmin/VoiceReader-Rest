import os
import pytest

from flask import Flask
from voicereader import startup


@pytest.fixture(scope='function')
def flask_app():
    flask = Flask(__name__)
    flask.config['TESTING'] = True
    flask.config['ENV'] = 'testing'

    return flask


@pytest.fixture
def test_envs():
    envs = {
        'TEST_CONFIG_ENV': 'testing',
        'TEST_CONFIG_PING': 'PONG'
    }

    for key, val in envs.items():
        os.environ[key] = val

    yield envs

    for k, v in envs.items():
        os.environ.pop(k)


def test_load_config_from_json(flask_app):
    startup.load_config_from_json(flask_app, root='testdata/config')

    assert 'sub' == flask_app.config['JWT_IDENTITY_CLAIM']
    assert 'TEST KEY' == flask_app.config['JWT_SECRET_KEY']


def test_load_config_from_json_none_app():
    with pytest.raises(ValueError):
        startup.load_config_from_json(None)


def test_load_config_from_json_none_root(flask_app):
    with pytest.raises(ValueError):
        startup.load_config_from_json(flask_app, None)


def test_load_config_from_env(flask_app, test_envs):
    startup.load_config_from_env(flask_app, test_envs)

    for k, v in test_envs.items():
        assert v == flask_app.config[k]


def test_load_config_from_env_none_app(test_envs):
    with pytest.raises(ValueError):
        startup.load_config_from_env(None, test_envs)


def test_load_config_from_env_none_envs(flask_app):
    with pytest.raises(ValueError):
        startup.load_config_from_env(flask_app, None)
