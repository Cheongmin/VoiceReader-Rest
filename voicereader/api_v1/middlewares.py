from ..services import db
from ..services.jwt import Jwt
from ..services.s3_storage import S3Storage
from ..services.local_storage import LocalStorage

jwt = Jwt()
storage = LocalStorage()


def init_app(app):
    storage.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
