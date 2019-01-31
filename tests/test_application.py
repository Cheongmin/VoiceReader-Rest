from voicereader import application


def test_create():
    app = application.create()

    assert app is not None
