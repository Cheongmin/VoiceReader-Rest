import os


default_envs = {

}


def load_config(app, root='../', envs=default_envs):
    load_config_from_json(app, root)
    load_config_from_env(app, envs)


def load_config_from_json(app, root='../'):
    if not app:
        raise ValueError(app)

    if not root:
        raise ValueError(root)

    app.config.from_json(os.path.join(root, 'config.json'))
    app.config.from_json(os.path.join(root, 'config.{}.json'.format(app.config['ENV'])), True)


def load_config_from_env(app, envs):
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
