import json
import pytest
import io

from flask import jsonify
from flask_restplus import Api
from flask_jwt_extended import JWTManager, create_access_token

from pymongo.errors import DuplicateKeyError

from voicereader.api_v1.user import controller


@pytest.fixture(scope='function')
def flask_client(monkeypatch, flask_app, flask_client):
    flask_app.config['JWT_SECRET_KEY'] = 'testing_key'
    flask_app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'

    api = Api(flask_app, title='testing')
    api.add_namespace(controller.api, path='/users')

    jwt = JWTManager(flask_app)
    jwt._set_error_handler_callbacks(api)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            'message': error_string
        }), 401

    return flask_client


@pytest.fixture(scope='function')
def mock_access_token(monkeypatch, flask_client, flask_app):
    fake_user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: fake_user_id)

    with flask_app.app_context():
        return create_access_token(fake_user_id)


def test_user_create_success(monkeypatch, flask_client):
    expected_firebase_uid = 'firebase_uid'
    expected_email = 'example@example.exa'
    expected_display_name = 'example'

    mock_decoded_token = {
        'sub': expected_firebase_uid,
        'email': expected_email
    }

    class MockDb:
        class MockUsers:
            def insert(self, document):
                pass
        users = MockUsers()

    monkeypatch.setattr(controller.auth, 'verify_id_token', lambda id_token: mock_decoded_token)
    monkeypatch.setattr(controller.mongo, 'db', MockDb())

    headers = {
        'Authorization': 'VALID_ID_TOKEN',
        'Content-Type': 'application/json'
    }

    res = flask_client.post('/users', headers=headers, data=json.dumps({
        'display_name': expected_display_name
    }))

    payload = res.get_json()

    assert 201 == res.status_code
    assert payload['_id']
    assert expected_display_name == payload['display_name']
    assert expected_email == payload['email']
    assert expected_firebase_uid == payload['fcm_uid']
    assert payload['created_date']
    assert payload['picture']


def test_user_create_not_include_idtoken(monkeypatch, flask_client):
    headers = {
        'Content-Type': 'application/json'
    }

    res = flask_client.post('/users', headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_user_create_invalid_idtoken(monkeypatch, flask_client):
    def mock_verify_id_token(id_token):
        raise ValueError()

    monkeypatch.setattr(controller.auth, 'verify_id_token', mock_verify_id_token)

    headers = {
        'Authorization': 'INVALID_ID_TOKEN',
        'Content-Type': 'application/json'
    }

    res = flask_client.post('/users', headers=headers, data=json.dumps({
        'display_name': 'VALID_NAME'
    }))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_user_create_not_include_payload(monkeypatch, flask_client):
    headers = {
        'Authorization': 'VALID_ID_TOKEN'
    }

    res = flask_client.post('/users', headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_user_create_not_include_name(monkeypatch, flask_client):
    headers = {
        'Authorization': 'VALID_ID_TOKEN',
        'Content-Type': 'application/json'
    }

    res = flask_client.post('/users', headers=headers, data=json.dumps({}))

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_user_create_already_exists_user(monkeypatch, flask_client):
    class MockDb:
        class MockUsers:
            def insert(self, document):
                raise DuplicateKeyError(None)
        users = MockUsers()

    mock_decoded_token = {
        'sub': 'example',
        'email': 'example@example.exa'
    }

    monkeypatch.setattr(controller.auth, 'verify_id_token', lambda id_token: mock_decoded_token)
    monkeypatch.setattr(controller.mongo, 'db', MockDb())

    headers = {
        'Authorization': 'VALID_ID_TOKEN',
        'Content-Type': 'application/json'
    }

    res = flask_client.post('/users', headers=headers, data=json.dumps({
        'display_name': 'example name'
    }))

    assert res.status_code == 409
    assert res.get_json()['message']


def test_user_get_success(monkeypatch, mock_access_token, flask_client):
    expected_user_id = '5c41b34c18283823a809ef4b'

    class MockDb:
        class MockUsers:
            def find_one(self, query):
                if str(query['_id']) == expected_user_id:
                    return {
                        '_id': expected_user_id
                    }

                return None

        users = MockUsers()

    monkeypatch.setattr(controller.mongo, 'db', MockDb())

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('/users/{}'.format(expected_user_id), headers=headers)
    payload = res.get_json()

    assert 200 == res.status_code
    assert expected_user_id == payload['_id']


def test_user_get_not_include_accesstoken(flask_client):
    expected_user_id = 'VALID_USER_ID'

    res = flask_client.get('/users/{}'.format(expected_user_id))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_user_get_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_TOKEN')
    }

    res = flask_client.get('/users/{}'.format('VALID_USER_ID'), headers=headers)

    assert 401 == res.status_code


def test_user_get_not_object_id(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('/users/{}'.format('INVALID_USER_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_user_get_not_found(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockUsers:
            def find_one(self, query):
                return None

        users = MockUsers()

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('/users/{}'.format('NOT_FOUND_USER_ID'), headers=headers)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_user_update_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockUsers:
            def update_one(self, query, body):
                class MockResult:
                    matched_count = 1

                return MockResult()

        users = MockUsers()

    expected_user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.put('/users/{}'.format(expected_user_id), headers=headers, data=json.dumps({
        'display_name': 'example name'
    }))

    assert 200 == res.status_code


def test_user_update_not_include_accesstoken(flask_client):
    headers = {
        'Content-Type': 'application/json'
    }

    res = flask_client.put('/users/{}'.format('VALID_UESR_ID'), headers=headers, data=json.dumps({
        'display_name': 'example name'
    }))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_user_update_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN'),
        'Content-Type': 'application/json'
    }

    res = flask_client.put('/users/{}'.format('VALID_USER_ID'), headers=headers, data=json.dumps({
        'display_name': 'example name'
    }))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_user_update_not_include_payload(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('VALID_ACCESS_TOKEN')
    }

    res = flask_client.put('/users/{}'.format('VALID_USER_ID', headers=headers))

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_user_update_not_equal_userid(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.put('/users/{}'.format('NOT_EQUAL_USER_ID'), headers=headers, data=json.dumps({
        'display_name': 'example name'
    }))

    assert 403 == res.status_code
    assert res.get_json()['message']


def test_user_update_not_found_user(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockUsers:
            def update_one(self, query, body):
                class MockResult:
                    matched_count = 0

                return MockResult()

        users = MockUsers()

    expected_user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.put('/users/{}'.format(expected_user_id), headers=headers, data=json.dumps({
        'display_name': 'example name'
    }))

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_user_remove_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockUsers:
            def delete_one(self, query):
                class MockResult:
                    deleted_count = 1

                return MockResult()

        users = MockUsers()

    expected_user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('/users/{}'.format(expected_user_id), headers=headers)

    assert 204 == res.status_code


def test_user_remove_not_include_accesstoken(flask_client):
    res = flask_client.delete('/users/{}'.format('VALID_USER_ID'))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_user_remove_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'INVALID_ACCESS_TOKEN'
    }

    res = flask_client.delete('/users/{}'.format('VALID_USER_ID'), headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_user_remove_not_equal_userid(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
    }

    res = flask_client.delete('/users/{}'.format('NOT_EQUAL_USER_ID'), headers=headers)

    assert 403 == res.status_code
    assert res.get_json()['message']


def test_user_remove_not_found_user(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockUsers:
            def delete_one(self, query):
                class MockResult:
                    deleted_count = 0

                return MockResult()

        users = MockUsers()

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
    }

    res = flask_client.delete('/users/{}'.format('VALID_USER_ID'), headers=headers)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_get_user_questions_success(monkeypatch, flask_client, mock_access_token):


    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
    }

    res = flask_client.get('/users/{}/questions'.format('VALID_USER_ID'), headers=headers)

    assert 200 == res.status_code


def test_photo_upload_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockUsers:
            def update_one(self, idx, query):
                class MockResult:
                    matched_count = 1

                return MockResult()

        users = MockUsers()

    user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: user_id)
    monkeypatch.setattr(controller.storage, 'upload_file', lambda prefix, file: None)
    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    data = {
        'photo': (io.BytesIO(b"abc"), '00.jpg')
    }

    res = flask_client.post('/users/{}/photo'.format(user_id), headers=headers, data=data)

    assert 200 == res.status_code


def test_photo_upload_not_include_accesstoken(monkeypatch, flask_client):
    res = flask_client.post('/users/{}/photo'.format('VALID_USER_ID'))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_photo_upload_invalid_accesstoken(monkeypatch, flask_client):
    headers = {
        'Authoriztion': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.post('/users/{}/photo'.format('VALID_USER_ID'), headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_photo_upload_not_equal_userid(monkeypatch, flask_client, mock_access_token):
    user_id = 'NOT_EQUAL_USER_ID'

    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: 'VALID_USER_ID')

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.post('/users/{}/photo'.format(user_id), headers=headers)

    assert 403 == res.status_code
    assert res.get_json()['message']


def test_photo_upload_unsupport_media_type(monkeypatch, mock_access_token, flask_client):
    user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: user_id)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    data = {
        'photo': (io.BytesIO(b"abc"), '00.mp3')
    }

    res = flask_client.post('/users/{}/photo'.format(user_id), headers=headers, data=data)

    assert 415 == res.status_code
    assert res.get_json()['message']


def test_photo_upload_not_found_user(monkeypatch, mock_access_token, flask_client):
    class MockDb:
        class MockUsers:
            def update_one(self, idx, query):
                class MockResult:
                    matched_count = 0

                return MockResult()

        users = MockUsers()

    user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: user_id)
    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    data = {
        'photo': (io.BytesIO(b"abc"), '00.jpg')
    }

    res = flask_client.post('/users/{}/photo'.format(user_id), headers=headers, data=data)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_get_photo_success(monkeypatch, flask_client):
    expected_image_io = b'abc'
    expected_content_type = 'image'

    monkeypatch.setattr(controller.storage, 'fetch_file', lambda resource, name: (expected_image_io, name))

    res = flask_client.get('/users/00/photo/default_user_profile.png')

    assert 200 == res.status_code
    assert expected_content_type == res.headers['Content-Type']
    assert expected_image_io == res.data


def test_get_photo_not_found(monkeypatch, flask_client):
    monkeypatch.setattr(controller.storage, 'fetch_file', lambda resource, name: None)

    res = flask_client.get('/users/00/photo/NOT_EXISTS_PROFILE.png')

    assert 404 == res.status_code


def test_debug_get_users(monkeypatch, flask_client):
    class MockDb:
        class MockUsers:
            def find(self):
                return [
                    {
                        '_id': 'VALID_USER_ID_1',
                    },
                    {
                        '_id': 'VALID_USER_ID_2'
                    }
                ]

        users = MockUsers()

    expected_item_count = 2

    monkeypatch.setattr(controller.mongo, 'db', MockDb())

    res = flask_client.get('/users/debug')
    payload = res.get_json()

    assert 200 == res.status_code
    assert expected_item_count == len(payload)
