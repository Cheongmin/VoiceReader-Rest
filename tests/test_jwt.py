import pytest

from flask_jwt_extended import JWTManager, jwt_required
from voicereader.services.jwt import Jwt


def test_create():
    jwt = Jwt()

    assert isinstance(jwt._jwt_manager, JWTManager)


def test_init_app(flask_app, flask_client):
    jwt = Jwt()
    jwt.init_app(flask_app)

    @flask_app.route('/')
    @jwt_required
    def index():
        return ''

    res = flask_client.get('/')

    assert res.status_code == 401


def test_init_app_none_app():
    jwt = Jwt()

    with pytest.raises(ValueError):
        jwt.init_app(None)
