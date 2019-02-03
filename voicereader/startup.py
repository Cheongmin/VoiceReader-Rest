import os


default_envs = {
    "VOICEREADER_API_VERSION",

    "MONGO_URI",

    "JWT_SECRET_KEY",
    "JWT_ACCESS_TOKEN_EXPIRES_SEC",
    "JWT_REFRESH_TOKEN_EXPIRES_SEC",
    "JWT_IDENTITY_CLAIM",
    "JWT_ERROR_MESSAGE_KEY",

    "S3_BUCKET_NAME",
    "S3_REGION",
    "S3_KEY",
    "S3_SECRET",

    "FIREBASE_CONFIG_PATH",
}


def configure_app(app):
    from voicereader.extensions.json_encoder import JSONEncoder

    app.json_encoder = JSONEncoder


def load_config(app, root='../', envs=default_envs):
    _load_config_from_json(app, root)
    _load_config_from_env(app, envs)


def _load_config_from_json(app, root='../'):
    if not app:
        raise ValueError(app)

    if not root:
        raise ValueError(root)

    app.config.from_json(os.path.join(root, 'config.json'))
    app.config.from_json(os.path.join(root, 'config.{}.json'.format(app.config['ENV'])), True)


def _load_config_from_env(app, envs):
    if not app:
        raise ValueError(app)

    if not envs:
        raise ValueError(envs)

    for k in envs:
        env = os.environ.get(k)

        if env is None:
            env = app.config.get(k)

            if env is None:
                continue

        app.config[k] = env


def register_resources(app):
    from .api_common import resource as common_resource
    from .api_v1 import resource as v1_resource

    resources = [
        common_resource,
        v1_resource,
    ]

    for resource in resources:
        resource.init_app(app)
