from voicereader.api_common.controller import blueprint


def test_home(flask_app, flask_client):
    flask_app.register_blueprint(blueprint)

    res = flask_client.get('/')

    assert res.status_code == 302


def test_ping(flask_app, flask_client):
    flask_app.register_blueprint(blueprint)

    res = flask_client.get('/api/ping')

    assert res.status_code == 200
    assert res.get_data() == b'pong'

    res = flask_client.get('/api/ping/')

    assert res.status_code == 200
    assert res.get_data() == b'pong'


def test_get_version(flask_app, flask_client):
    flask_app.register_blueprint(blueprint)

    res = flask_client.get('/api/info/version')

    assert res.status_code == 200
    assert res.get_data() == b'testing version'

    res = flask_client.get('/api/info/version/')

    assert res.status_code == 200
    assert res.get_data() == b'testing version'


def test_get_version_exists_version(flask_app, flask_client):
    flask_app.config['VERSION_PATH'] = 'tests/testdata/VERSION'
    flask_app.register_blueprint(blueprint)

    res = flask_client.get('/api/info/version')

    assert res.status_code == 200
    assert res.get_data() == b'v0.0.0'


def test_get_env(flask_app, flask_client):
    flask_app.register_blueprint(blueprint)

    res = flask_client.get('/api/info/env')

    assert res.status_code == 200
    assert res.get_data() == b'testing'

    res = flask_client.get('/api/info/env/')

    assert res.status_code == 200
    assert res.get_data() == b'testing'
