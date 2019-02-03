import os
import pytest

from voicereader import startup


@pytest.fixture
def test_envs():
    envs = {
        'TEST_CONFIG_ENV': 'testing',
        'TEST_CONFIG_PING': 'PONG'
    }

    for key, val in envs.items():
        os.environ[key] = val

    yield envs

    for k in envs.keys():
        os.environ.pop(k)


def test_configure_app(flask_app):
    from voicereader.extensions.json_encoder import JSONEncoder

    startup.configure_app(flask_app)

    assert isinstance(flask_app.json_encoder, type(JSONEncoder))


def test_load_config(flask_app, test_envs):
    startup.load_config(flask_app, 'testdata/config', test_envs)

    assert 'sub' == flask_app.config['JWT_IDENTITY_CLAIM']
    assert 'TEST KEY' == flask_app.config['JWT_SECRET_KEY']

    for k, v in test_envs.items():
        assert v == flask_app.config[k]


def test_load_config_none_app():
    with pytest.raises(ValueError):
        startup.load_config(None)


def test_load_config_not_found_config(flask_app):
    with pytest.raises(FileNotFoundError):
        startup.load_config(flask_app, root='NOT/EXISTS/PATH')


# def test_load_config_none_root(flask_app):
#     with pytest.raises(ValueError):
#         startup.load_config(flask_app, root=None)
#
#
# def test_load_config_none_envs(flask_app):
#     with pytest.raises(ValueError):
#         startup.load_config(flask_app, envs=None)


def test_load_config_from_json(flask_app):
    startup._load_config_from_json(flask_app, root='testdata/config')

    assert 'sub' == flask_app.config['JWT_IDENTITY_CLAIM']
    assert 'TEST KEY' == flask_app.config['JWT_SECRET_KEY']


def test_load_config_from_json_not_found_config(flask_app):
    with pytest.raises(FileNotFoundError):
        startup._load_config_from_json(flask_app, root='NOT/EXISTS/PATH')


def test_load_config_from_json_none_app():
    with pytest.raises(ValueError):
        startup._load_config_from_json(None)


def test_load_config_from_json_none_root(flask_app):
    with pytest.raises(ValueError):
        startup._load_config_from_json(flask_app, None)


def test_load_config_from_env(flask_app, test_envs):
    startup._load_config_from_env(flask_app, test_envs)

    for k, v in test_envs.items():
        assert v == flask_app.config[k]


def test_load_config_from_env_none_app(test_envs):
    with pytest.raises(ValueError):
        startup._load_config_from_env(None, test_envs)


def test_load_config_from_env_none_envs(flask_app):
    with pytest.raises(ValueError):
        startup._load_config_from_env(flask_app, None)


def test_register_resources(monkeypatch, flask_app, flask_client):
    monkeypatch.setattr('voicereader.api_v1.middlewares.init_app', lambda app: None)
    monkeypatch.setattr('voicereader.api_v1.middlewares.jwt.init_api', lambda api: None)

    startup.register_resources(flask_app)

    res = flask_client.get('api/ping')

    assert res.status_code == 200
    assert res.get_data() == b'pong'
