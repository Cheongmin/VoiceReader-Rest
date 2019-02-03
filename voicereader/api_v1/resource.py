from . import middlewares
from .blueprint import blueprint, api


def init_app(app):
    middlewares.init_app(app)
    middlewares.jwt.init_api(api)

    app.register_blueprint(blueprint)
