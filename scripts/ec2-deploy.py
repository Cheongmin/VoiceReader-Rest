import os

from fabric.api import run, env, put
from fabric.context_managers import cd

env.user = os.getenv('EC2_USER')
env.hosts = os.getenv('EC2_HOST')
env.key_filename = 'voicereader-vm.pem'

src = 'voicereader-rest/'


def deploy():
    set_env()

    run('mkdir -p {}'.format(src))

    put('nginx.conf', src)
    put('stack-compose.yml', src)
    put('scripts/swarm-deploy.sh', src)

    with cd(src):
        run('bash swarm-deploy.sh')


def set_env():
    deploy_stack_name = os.getenv('DEPLOY_STACK_NAME')
    docker_user_name = os.getenv('DOCKER_USERNAME')
    docker_image_name = os.getenv('DOCKER_IMAGE')
    container_api_name = os.getenv('CONTAINER_API_NAME')

    run('export DEPLOY_STACK_NAME={}'.format(deploy_stack_name))
    run('export DOCKER_USERNAME={}'.format(docker_user_name))
    run('export DOCKER_IMAGE_NAME={}'.format(docker_image_name))
    run('export CONTAINER_API_NAME={}'.format(container_api_name))
