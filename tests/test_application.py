from voicereader import application


def test_create(monkeypatch):
    monkeypatch.setattr('voicereader.api_v1.middlewares.init_app', lambda app: None)
    monkeypatch.setattr('voicereader.api_v1.middlewares.jwt.init_api', lambda api: None)

    app = application.create()
    res = app.test_client().get('api/ping')

    assert res.status_code == 200
    assert res.get_data() == b'pong'
