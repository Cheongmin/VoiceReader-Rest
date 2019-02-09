import pytest

from voicereader.api_v1.user import repository
from voicereader.extensions.errors import InvalidIdError


@pytest.fixture(scope='function')
def mock_db():
    class MockDb:
        class MockUsers:
            def find_one(self, query):
                return {}

        users = MockUsers()

    return MockDb()


def test_get_user_success(monkeypatch, mock_db):
    expected_user_id = 'VALID_USER_ID'
    expected_user = {
        '_id': expected_user_id
    }

    monkeypatch.setattr(mock_db.users, 'find_one', lambda query: expected_user)
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    actual_user = repository.get_user_by_id(expected_user_id)

    assert expected_user == actual_user


def test_get_user_not_found(monkeypatch, mock_db):
    expected_user = None
    argument_user_id = 'NOT_EXISTS_USER_ID'

    monkeypatch.setattr(mock_db.users, 'find_one', lambda query: expected_user)
    monkeypatch.setattr(repository, 'ObjectId', lambda value: value)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    actual_user = repository.get_user_by_id(argument_user_id)

    assert expected_user == actual_user


def test_get_user_invalid_id(monkeypatch, mock_db):
    invalid_user_id = 'INVALID_USER_ID'

    with pytest.raises(InvalidIdError):
        repository.get_user_by_id(invalid_user_id)


def test_get_user_id_by_firebase_uid_success(monkeypatch, mock_db):
    valid_firebase_uid = 'VALID_FIREBASE_UID'
    expected_user_id = 'EXISTS_USER_ID'

    monkeypatch.setattr(mock_db.users, 'find_one', lambda query: {'_id': expected_user_id})
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    actual_user_id = repository.get_user_id_by_firebase_uid(valid_firebase_uid)

    assert expected_user_id == actual_user_id


def test_get_user_id_by_firebase_uid_not_found(monkeypatch, mock_db):
    expected_user_id = None
    not_found_firebase_uid = 'NOT_FOUND_FIREBASE_UID'

    monkeypatch.setattr(mock_db.users, 'find_one', lambda query: None)
    monkeypatch.setattr(repository.mongo, 'db', mock_db)

    actual_user_id = repository.get_user_id_by_firebase_uid(not_found_firebase_uid)

    assert expected_user_id == actual_user_id
