from voicereader.api_v1 import resource


def test_init_app(monkeypatch, flask_app, flask_client):
    monkeypatch.setattr(resource.middlewares, 'init_app', lambda app: None)
    monkeypatch.setattr(resource.middlewares.jwt, 'init_api', lambda api: None)

    resource.init_app(flask_app)
