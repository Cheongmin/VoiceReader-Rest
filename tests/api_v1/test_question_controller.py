import pytest
import io

from flask import jsonify
from flask_restplus import Api
from flask_jwt_extended import JWTManager, create_access_token

from voicereader.api_v1.question import controller


@pytest.fixture(scope='function')
def flask_client(monkeypatch, flask_app, flask_client):
    flask_app.config['JWT_SECRET_KEY'] = 'testing_key'
    flask_app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'

    api = Api(flask_app, title='testing')
    api.add_namespace(controller.api, path='/questions')

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


def test_get_questions_success(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller.question_repository, 'get_questions', lambda offset, size: {})

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions', headers=headers)

    assert 200 == res.status_code


def test_get_questions_not_include_accesstoken(flask_client):
    res = flask_client.get('questions')

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_get_questions_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.get('questions', headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_create_question_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockQuestions:
            def insert(self):
                return {}

        questions = MockQuestions

    monkeypatch.setattr(controller, 'ObjectId', lambda value=None: value)
    monkeypatch.setattr(controller.user_repository, 'get_user_by_id', lambda user_id: {})
    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller.storage, 'upload_file', lambda resource, file: None)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    form = {
        'title': 'example title',
        'contents': 'example contents',
        'subtitles': 'example subtitles',
        'sound': (io.BytesIO(b"abc"), '00.mp3')
    }

    res = flask_client.post('questions', headers=headers, data=form)

    assert 201 == res.status_code


def test_create_question_not_include_accesstoken(flask_client):
    res = flask_client.post('questions')

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_create_question_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.post('questions', headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_create_question_unsupport_media_type(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value=None: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    form = {
        'title': 'example title',
        'contents': 'example contents',
        'subtitles': 'example subtitles',
        'sound': (io.BytesIO(b"abc"), '00.jpg')
    }

    res = flask_client.post('questions', headers=headers, data=form)

    assert 415 == res.status_code
    assert res.get_json()['message']


def test_get_question_success(monkeypatch, flask_client, mock_access_token):
    async def mock_add_read_to_question(a, b):
        pass

    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.user_repository, 'get_user_by_id', lambda user_id: {})
    monkeypatch.setattr(controller, 'add_read_to_question', mock_add_read_to_question)
    monkeypatch.setattr(controller.question_repository, 'get_question_by_id', lambda que_id: {
        'writer_id': 'VALID_USER_ID'
    })

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}'.format('VALID_QUESTION_ID'), headers=headers)

    assert 200 == res.status_code


def test_get_question_not_include_accesstoken(flask_client):
    res = flask_client.get('questions/{}'.format('VALID_QUESTION_ID'))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_get_question_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.get('questions/{}'.format('VALID_QUESTION_ID'), headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_get_question_invalid_questionid(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}'.format('INVALID_QUESTION_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_get_question_not_found_question(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.question_repository, 'get_question_by_id', lambda que_id: None)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}'.format('NOT_FOUND_QUESTION_ID'), headers=headers)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_remove_question_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockQuestions:
            def delete_one(self):
                return {}

        questions = MockQuestions

    user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: user_id)
    monkeypatch.setattr(controller.question_repository, 'get_question_by_id', lambda que_id: {
        'writer_id': user_id
    })

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}'.format('VALID_QUESTION_ID'), headers=headers)

    assert 204 == res.status_code


def test_remove_question_not_include_accesstoken(flask_client):
    res = flask_client.delete('questions/{}'.format('VALID_QUESTION_ID'))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_remove_question_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.delete('questions/{}'.format('VALID_QUESTION_ID'), headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_remove_question_invalid_questionid(monkeypatch, flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}'.format('INVALID_QUESTION_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_remove_question_not_found_question(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.question_repository, 'get_question_by_id', lambda que_id: None)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}'.format('INVALID_QUESTION_ID'), headers=headers)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_remove_question_not_equal_userid(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.question_repository, 'get_question_by_id', lambda que_id: {
        'writer_id': 'NOT_EQUAL_USER_ID'
    })

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}'.format('INVALID_QUESTION_ID'), headers=headers)

    assert 403 == res.status_code
    assert res.get_json()['message']


def test_get_sound_success(monkeypatch, flask_client):
    expected_audio_io = b'abc'
    expected_content_type = 'audio'

    monkeypatch.setattr(controller.storage, 'fetch_file', lambda resource, name: (expected_audio_io, name))

    res = flask_client.get('questions/sound/EXIST_FILE.mp3')

    assert 200 == res.status_code
    assert expected_content_type == res.headers['Content-Type']
    assert expected_audio_io == res.data


def test_get_sound_not_found(monkeypatch, flask_client):
    monkeypatch.setattr(controller.storage, 'fetch_file', lambda resource, name: None)

    res = flask_client.get('questions/sound/NOT_EXIST_FILE.mp3')

    assert 404 == res.status_code

