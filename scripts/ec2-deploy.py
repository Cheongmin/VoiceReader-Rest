import os

from fabric.api import local, run, sudo, env, put
from fabric.context_managers import cd

env.user = os.getenv('EC2_USER')
env.hosts = os.getenv('EC2_HOST')

src = 'voicereader-rest/'


def deploy():
    local('sudo ssh-agent bash')
    local('ssh-add voicereader-vm.pem')

    run('mkdir -p {}'.format(src))

    put('nginx.conf', src)
    put('stack-compose.yml', src)
    put('scripts/update-secrets.sh', src)
    put('scripts/swarm-deploy.sh', src)

    with cd(src):
        run('bash swarm-deploy.sh')
