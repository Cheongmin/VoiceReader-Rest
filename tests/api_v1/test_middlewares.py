from voicereader.api_v1 import middlewares


class Mock:
    def init_app(self, app):
        pass


def test_init_app(monkeypatch, flask_app):
    monkeypatch.setattr(middlewares, 'jwt', Mock())
    monkeypatch.setattr(middlewares, 'storage', Mock())
    monkeypatch.setattr(middlewares, 'db', Mock())

    middlewares.init_app(flask_app)
