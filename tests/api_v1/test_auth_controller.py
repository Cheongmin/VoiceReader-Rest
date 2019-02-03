import pytest

from flask import jsonify
from flask_jwt_extended import JWTManager, create_refresh_token
from flask_restplus import Api

from voicereader.api_v1.auth import controller


@pytest.fixture(scope='function')
def flask_client(monkeypatch, flask_app, flask_client):
    flask_app.config['JWT_SECRET_KEY'] = 'testing_key'

    api = Api(flask_app, title='testing')
    api.add_namespace(controller.api, path='/oauth2')

    jwt = JWTManager(flask_app)
    jwt._set_error_handler_callbacks(api)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            'message': error_string
        }), 401

    return flask_client


def test_access_token_expire_delta(flask_app):
    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES_SEC'] = 3600

    with flask_app.app_context():
        assert controller._access_token_expire_delta()


def test_access_token_expire_in(flask_app):
    expected_expire_in = 3600

    flask_app.config['JWT_ACCESS_TOKEN_EXPIRES_SEC'] = expected_expire_in

    with flask_app.app_context():
        assert expected_expire_in == controller._access_token_expire_in()


def test_refresh_token_expire_delta(flask_app):
    flask_app.config['JWT_REFRESH_TOKEN_EXPIRES_SEC'] = 3600

    with flask_app.app_context():
        assert controller._refresh_token_expire_delta()


def test_refresh_token_expire_in(flask_app):
    expected_expire_in = 3600

    flask_app.config['JWT_REFRESH_TOKEN_EXPIRES_SEC'] = expected_expire_in

    with flask_app.app_context():
        assert expected_expire_in == controller._refresh_token_expire_in()


def test_get_success(monkeypatch, flask_client):
    expected_token_type = 'Bearer'
    expected_access_token = 'access_token'
    expected_refresh_token = 'refresh_token'
    expected_expire_in = 3600

    monkeypatch.setattr(controller.auth, 'verify_id_token', lambda token, app: {'sub': 'user_id'})
    monkeypatch.setattr(controller, 'get_user_id', lambda uid: 'exists user_id')
    monkeypatch.setattr(controller, 'create_access_token', lambda user_id, expires_delta: expected_access_token)
    monkeypatch.setattr(controller, 'create_refresh_token', lambda user_id, expires_delta: expected_refresh_token)
    monkeypatch.setattr(controller, '_access_token_expire_delta', lambda: None)
    monkeypatch.setattr(controller, '_refresh_token_expire_delta', lambda: None)
    monkeypatch.setattr(controller, '_access_token_expire_in', lambda: expected_expire_in)

    headers = {"Authorization": "VALID_ID_TOKEN"}

    res = flask_client.get('/oauth2/token', headers=headers)
    payload = res.get_json()

    assert 200 == res.status_code
    assert expected_token_type == payload['type']
    assert expected_access_token == payload['access_token']
    assert expected_refresh_token == payload['refresh_token']
    assert expected_expire_in == payload['expire_in']


def test_get_not_include_idtoken(flask_client):
    res = flask_client.get('/oauth2/token')

    assert res.status_code == 400


def test_get_invalid_idtoken(flask_client):
    headers = {
        "Authorization": "INVALID_ID_TOKEN"
    }

    res = flask_client.get('/oauth2/token', headers=headers)

    assert res.status_code == 401


def test_get_not_registered_user(monkeypatch, flask_client):
    headers = {
        "Authorization": "VALID_ID_TOKEN"
    }

    monkeypatch.setattr(controller.auth, 'verify_id_token', lambda token, app: {'sub': 'user_id'})
    monkeypatch.setattr(controller, 'get_user_id', lambda uid: None)

    res = flask_client.get('/oauth2/token', headers=headers)

    assert res.status_code == 404


def test_post_success(monkeypatch, flask_app, flask_client):
    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: 'EXISTS_USER_ID')
    monkeypatch.setattr(controller, 'create_access_token', lambda user_id, expires_delta: None)
    monkeypatch.setattr(controller, '_access_token_expire_delta', lambda: None)
    monkeypatch.setattr(controller, '_access_token_expire_in', lambda: None)

    def mock_refresh_token():
        with flask_app.app_context():
            return create_refresh_token('EXISTS_USER_ID')

    headers = {
        "Authorization": 'Bearer {}'.format(mock_refresh_token())
    }

    res = flask_client.post('/oauth2/token', headers=headers)

    assert res.status_code == 200


def test_post_not_include_refreshtoken(monkeypatch, flask_client):
    res = flask_client.post('/oauth2/token')

    assert res.status_code == 401


def test_post_invalid_refreshtoken(flask_client):
    headers = {
        'Authorization': "INVALID_TOKEN"
    }

    res = flask_client.post('/oauth2/token', headers=headers)
    payload = res.get_json()

    assert res.status_code == 401
    assert payload['message']


def test_debug_get_success(monkeypatch, flask_client):
    monkeypatch.setattr(controller, 'get_user', lambda user_id: {'user_id': 'EXISTS_USER_ID'})
    monkeypatch.setattr(controller, 'create_access_token', lambda user_id, expires_delta: 'refresh_token')
    monkeypatch.setattr(controller, '_access_token_expire_delta', lambda: None)

    res = flask_client.get('/oauth2/token/debug?user_id=USER_ID')
    payload = res.get_json()

    assert res.status_code == 200
    assert payload['access_token']
