import os

from fabric.api import run, env, put
from fabric.context_managers import cd

env.user = os.getenv('EC2_USER')
env.hosts = os.getenv('EC2_HOST')
env.key_filename = 'voicereader-vm.pem'

src = 'voicereader-rest/'


def deploy():
    run('mkdir -p {}'.format(src))

    put('nginx.conf', src)
    put('stack-compose.yml', src)
    put('scripts/swarm-deploy.sh', src)

    with cd(src):
        run('bash swarm-deploy.sh')
