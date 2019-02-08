import os
from fabric.api import run, env, put
from fabric.context_managers import cd, shell_env

env.user = os.getenv('EC2_USER')
env.hosts = os.getenv('EC2_HOST')
env.key_filename = os.getenv('EC2_KEY_PATH')

src = 'voicereader-rest/'


def deploy(target_version):
    run('mkdir -p {}'.format(src))

    put('nginx.conf', src)
    put('stack-compose.yml', src)
    put('scripts/deploy_docker_swarm.sh', src)

    with cd(src):
        with shell_env(DOCKER_USERNAME=os.getenv('DOCKER_USERNAME'),
                       DOCKER_IMAGE_NAME=os.getenv('DOCKER_IMAGE_NAME'),
                       DEPLOY_APP_VERSION=target_version):
            run('bash deploy_docker_swarm.sh {}'.format(target_version))
