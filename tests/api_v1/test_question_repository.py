import pytest

from voicereader.api_v1.question import repository


@pytest.fixture(scope='function')
def mock_db():
    class MockDb:
        class MockQuestions:
            def aggregate(self, query):
                return []

        questions = MockQuestions

    return MockDb()


def test_get_questions(monkeypatch, mock_db):
    monkeypatch.setattr(mock_db.questions, 'aggregate', lambda query: [{'_id': 'VALID_QUESTION_ID'}])
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    result = repository.get_questions(0, 3)

    assert result


def test_get_question_by_id(monkeypatch, mock_db):
    monkeypatch.setattr(mock_db.questions, 'aggregate', lambda query: [{'_id': 'VALID_QUESTION_ID'}])
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    result = repository.get_question_by_id('VALID_QUESTION_ID')

    assert result


def test_get_questions_by_user_id(monkeypatch, mock_db):
    monkeypatch.setattr(mock_db.questions, 'aggregate', lambda query: [{'_id': 'VALID_QUESTION_ID'}])
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    result = repository.get_questions_by_user_id('VALID_USER_ID')

    assert result
