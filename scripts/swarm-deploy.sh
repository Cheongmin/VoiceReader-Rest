#!/usr/bin/env bash

if sudo docker stack ls --format '{{.Name}}' | grep -Eq "^${DEPLOY_STACK_NAME}\$"; then
  docker pull ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:latest
  docker service update --image ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME} ${DEPLOY_STACK_NAME}_${CONTAINER_API_NAME}
else
  docker stack deploy -c stack-compose.yml ${DEPLOY_STACK_NAME}
fi

# docker rm $(docker ps -aq --filter "status=exited")
# docker rmi $(docker images -q --filter "dangling=true")
docker system prune -f