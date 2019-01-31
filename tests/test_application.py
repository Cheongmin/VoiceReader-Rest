from voicereader import application, startup


def test_create(monkeypatch):
    monkeypatch.setattr(startup, 'configure_middleware', lambda x: None)

    app = application.create()

    assert app is not None
