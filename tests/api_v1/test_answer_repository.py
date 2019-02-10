import pytest

from voicereader.api_v1.answer import repository
from voicereader.extensions.errors import InvalidIdError


@pytest.fixture(scope='function')
def mock_db():
    class MockDb:
        class MockAnswers:
            def find(self, query):
                return {}

            def find_one(self, query):
                return {}
        answers = MockAnswers

    return MockDb()


def test_get_answer_by_id_success(monkeypatch, mock_db):
    monkeypatch.setattr(mock_db.answers, 'find_one', lambda query: {'answers': [{'_id': 'VALID_ANSWER_ID'}]})
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    res = repository.get_answer_by_id('VALID_QUESTION_ID', 'NOT_FOUND_ANSWER_ID')

    assert res


def test_get_answer_by_id_not_found(monkeypatch, mock_db):
    expected = None

    monkeypatch.setattr(mock_db.answers, 'find_one', lambda query: expected)
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    actual = repository.get_answer_by_id('VALID_QUESTION_ID', 'VALID_ANSWER_ID')

    assert expected == actual


def test_get_answers_by_question_id_success(monkeypatch, mock_db):
    expected_question_id = 'VALID_USER_ID'
    expected = [{
        '_id': 'VALID_ANSWER_ID',
        'question_id': expected_question_id
    }]

    monkeypatch.setattr(mock_db.answers, 'find', lambda query: expected)
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    actual = repository.get_answers_by_question_id(expected_question_id)

    assert expected == actual


def test_get_answers_by_user_id_success(monkeypatch, mock_db):
    expected_user_id = 'VALID_USER_ID'
    expected = [{
        '_id': 'VALID_ANSWER_ID',
        'writer_id': expected_user_id
    }]

    monkeypatch.setattr(mock_db.answers, 'find', lambda query: expected)
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    actual = repository.get_answers_by_question_id(expected_user_id)

    assert expected == actual
