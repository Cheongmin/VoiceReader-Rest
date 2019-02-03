from flask import Flask
from . import startup


def create():
    app = Flask(__name__)

    startup.load_config(app)
    startup.configure_app(app)
    startup.register_resources(app)

    return app
