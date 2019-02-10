import pytest
import json

from flask import jsonify
from flask_restplus import Api
from flask_jwt_extended import JWTManager, create_access_token

from pymongo.errors import InvalidId

from voicereader.api_v1.answer import controller


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


def test_get_answers_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockQuestions:
            def find_one(self):
                return {
                    '_id': 'VALID_QUESTION_ID',
                    'answers': [
                        {'_id': 'VALID_ANSWER_ID_1', 'writer_id': 'VALID_USER_ID_1'},
                        {'_id': 'VALID_ANSWER_ID_2', 'writer_id': 'VALID_USER_ID_2'},
                    ]
                }

        questions = MockQuestions

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.user_repository, 'get_user_by_id', lambda user_id: None)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}/answers'.format('VALID_QUESTION_ID'), headers=headers)

    assert 200 == res.status_code


def test_get_answers_not_include_accesstoken(flask_client):
    res = flask_client.get('questions/{}/answers'.format('VALID_QUESTION_ID'))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_get_answers_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.get('questions/{}/answers'.format('VALID_QUESTION_ID'), headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_get_answers_invalid_questionid(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}/answers'.format('INVALID_QUESTION_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_get_answers_not_found_question(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockQuestions:
            def find_one(self):
                return None

        questions = MockQuestions

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}/answers'.format('VALID_QUESTION_ID'), headers=headers)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_create_answer_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockQuestions:
            def update_one(self, query):
                class MockResult:
                    modified_count = 1

                return MockResult()

        questions = MockQuestions

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller.user_repository, 'get_user_by_id', lambda user_id: {})
    monkeypatch.setattr(controller, 'ObjectId', lambda value=None: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.post('questions/{}/answers'.format('VALID_QUESTION_ID'), headers=headers, data=json.dumps({
        'contents': 'example'
    }))

    assert 201 == res.status_code


def test_create_answer_not_include_accesstoken(flask_client):
    headers = {
        'Content-Type': 'application/json'
    }

    res = flask_client.post('questions/{}/answers'.format('VALID_QUESTION_ID'), headers=headers, data=json.dumps({
        'contents': 'example'
    }))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_create_answer_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN'),
        'Content-Type': 'application/json'
    }

    res = flask_client.post('questions/{}/answers'.format('INVALID_QUESTION_ID'), headers=headers, data=json.dumps({
        'contents': 'example'
    }))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_create_answer_invalid_questionid(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.post('questions/{}/answers'.format('INVALID_QUESTION_ID'), headers=headers, data=json.dumps({
        'contents': 'example'
    }))

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_create_answer_not_include_payload(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.post('questions/{}/answers'.format('VALID_QUESTION_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_create_answer_invalid_payload(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.post('questions/{}/answers'.format('VALID_QUESTION_ID'), headers=headers, data=json.dumps({
        'invalid_contents_key': 'example'
    }))

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_create_answer_not_found_question(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockQuestions:
            def update_one(self, query):
                class MockResult:
                    modified_count = 0

                return MockResult()

        questions = MockQuestions

    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller, 'ObjectId', lambda value=None: value)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token),
        'Content-Type': 'application/json'
    }

    res = flask_client.post('questions/{}/answers'.format('NOT_FOUND_QUESTION_ID'),
                            headers=headers, data=json.dumps({'contents': 'example'}))

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_get_answer_success(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.user_repository, 'get_user_by_id', lambda user_id: {})
    monkeypatch.setattr(controller.answer_repository, 'get_answer_by_id', lambda que_id, ans_id: {
        '_id': ans_id,
        'question_id': que_id,
        'writer_id': 'VALID_USER_ID'
    })

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}/answers/{}'.format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 200 == res.status_code


def test_get_answer_not_include_accesstoken(flask_client):
    res = flask_client.get('questions/{}/answers/{}'.format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_get_answer_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.get('questions/{}/answers/{}'.format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_get_answer_invalid_questionid(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}/answers/{}'.format('INVALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_get_answer_invalid_answerid(monkeypatch, flask_client, mock_access_token):
    def mock_ObjectId(value):
        if value == 'VALID_QUESTION_ID':
            return value

        raise InvalidId(None)

    monkeypatch.setattr(controller, 'ObjectId', mock_ObjectId)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}/answers/{}'.format('VALID_QUESTION_ID', 'INVALID_ANSWER_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_get_answer_not_found_answer(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.answer_repository, 'get_answer_by_id', lambda que_id, ans_id: None)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.get('questions/{}/answers/{}'.format('VALID_QUESTION_ID', 'NOT_FOUND_ANSWER_ID'), headers=headers)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_remove_answer_success(monkeypatch, flask_client, mock_access_token):
    class MockDb:
        class MockQuestions:
            def update_one(self, query):
                class MockResult:
                    modified_count = 1

                return MockResult()

        questions = MockQuestions

    user_id = 'VALID_USER_ID'

    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller, 'get_jwt_identity', lambda: user_id)
    monkeypatch.setattr(controller.mongo, 'db', MockDb())
    monkeypatch.setattr(controller.answer_repository, 'get_answer_by_id', lambda que_id, ans_id: {
        '_id': ans_id,
        'question_id': que_id,
        'writer_id': user_id
    })

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}/answers/{}'
                              .format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 204 == res.status_code


def test_remove_answer_not_include_accesstoken(flask_client):
    res = flask_client.delete('questions/{}/answers/{}'.format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'))

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_remove_answer_invalid_accesstoken(flask_client):
    headers = {
        'Authorization': 'Bearer {}'.format('INVALID_ACCESS_TOKEN')
    }

    res = flask_client.delete('questions/{}/answers/{}'
                              .format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 401 == res.status_code
    assert res.get_json()['message']


def test_remove_answer_invalid_questionid(flask_client, mock_access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}/answers/{}'
                              .format('INVALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_remove_answer_invalid_answerid(monkeypatch, flask_client, mock_access_token):
    def mock_ObjectId(value):
        if value == 'VALID_QUESTION_ID':
            return value

        raise InvalidId(None)

    monkeypatch.setattr(controller, 'ObjectId', mock_ObjectId)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}/answers/{}'
                              .format('VALID_QUESTION_ID', 'INVALID_ANSWER_ID'), headers=headers)

    assert 400 == res.status_code
    assert res.get_json()['message']


def test_remove_answer_not_found_answer(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.answer_repository, 'get_answer_by_id', lambda que_id, ans_id: None)

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}/answers/{}'
                              .format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 404 == res.status_code
    assert res.get_json()['message']


def test_remove_answer_not_equal_userid(monkeypatch, flask_client, mock_access_token):
    monkeypatch.setattr(controller, 'ObjectId', lambda value: value)
    monkeypatch.setattr(controller.answer_repository, 'get_answer_by_id', lambda que_id, ans_id: {
        'writer_id': 'NOT_EQUAL_USER_ID'
    })

    headers = {
        'Authorization': 'Bearer {}'.format(mock_access_token)
    }

    res = flask_client.delete('questions/{}/answers/{}'
                              .format('VALID_QUESTION_ID', 'VALID_ANSWER_ID'), headers=headers)

    assert 403 == res.status_code
    assert res.get_json()['message']
