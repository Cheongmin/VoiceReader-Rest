#!/usr/bin/env bash


DOCKER_USERNAME=gyuhwankim
DOCKER_IMAGE_NAME=voicereader-rest
DEPLOY_STACK_NAME=voicereader-rest
CONTAINER_API_NAME=api


docker pull ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:latest

if sudo docker stack ls --format '{{.Name}}' | grep -Eq "^${DEPLOY_STACK_NAME}\$"; then
  docker service update --image ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME} ${DEPLOY_STACK_NAME}_${CONTAINER_API_NAME}
else
  docker stack deploy -c stack-compose.yml ${DEPLOY_STACK_NAME}
fi

# docker rm $(docker ps -aq --filter "status=exited")
# docker rmi $(docker images -q --filter "dangling=true")
docker system prune -f