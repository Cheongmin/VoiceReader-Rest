from ..services import db
from ..services.jwt import Jwt
from ..services.s3_storage import S3Storage

jwt = Jwt()
storage = S3Storage()


def init_app(app):
    storage.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
