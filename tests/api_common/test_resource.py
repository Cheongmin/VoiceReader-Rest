from voicereader.api_common import resource


def test_init_app(flask_app, flask_client):
    resource.init_app(flask_app)

    res = flask_client.get('api/ping')

    assert res.status_code == 200
    assert res.get_data() == b'pong'
