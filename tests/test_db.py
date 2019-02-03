import pytest


class MockMongo:
    class MockDb:
        class MockUsers:
            def create_index(self, x, unique):
                pass

        users = MockUsers()

    db = MockDb()

    def init_app(self, app):
        pass


def test_init_app(monkeypatch, flask_app):
    from voicereader.services import db

    monkeypatch.setattr(db, 'mongo', MockMongo())

    db.init_app(flask_app)


def test_init_app_none_app():
    from voicereader.services import db

    with pytest.raises(ValueError):
        db.init_app(None)
