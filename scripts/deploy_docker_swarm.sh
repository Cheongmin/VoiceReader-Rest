#!/usr/bin/env bash
# Require envvars
# DOCKER_USERNAME
# DOCKER_IMAGE_NAME


if [[ -z $1 ]]; then
    echo "Can't get version"
    exit 1
fi

TARGET_VERSION=$1
DEPLOY_STACK_NAME=voicereader-rest
CONTAINER_API_NAME=api

# Pull docker image from docker registry
docker pull ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${TARGET_VERSION}
if [[ $? != 0 ]]; then
    exit 2
fi


# Update docker container
if sudo docker stack ls --format '{{.Name}}' | grep -Eq "^${DEPLOY_STACK_NAME}\$"; then
  docker service update --image ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${TARGET_VERSION} ${DEPLOY_STACK_NAME}_${CONTAINER_API_NAME}
else
  docker stack deploy -c stack-compose.yml ${DEPLOY_STACK_NAME}
fi

if [[ $? != 0 ]]; then
    echo "Failed to deploy..."
    exit 2
fi

# Remove all unused resources.
docker system prune -f