import os

from fabric.api import local, run, sudo, env, put
from fabric.context_managers import cd

env.user = os.getenv('EC2_USER')
env.hosts = os.getenv('EC2_HOST')


def deploy():
    local('ssh-add voicereader-vm.pem')

    # run('mkdir VoiceReader-Rest-Production')

    sudo('docker service ls')
    pass
