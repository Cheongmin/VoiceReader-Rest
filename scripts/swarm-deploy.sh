#!/usr/bin/env bash

deploy_stack_name=voicereader-rest
docker_user_name=gyuhwankim
api_image_name=voicereader-rest

if sudo docker stack ls --format '{{.Name}}' | grep -Eq "^${deploy_stack_name}\$"; then
  docker pull ${docker_user_name}/${api_image_name}:latest

  docker service update --image ${docker_user_name}/${api_image_name} ${deploy_stack_name}_api

  docker rm $(docker ps -aq)
  docker rmi $(docker images -q --filter "dangling=true")
else
  docker stack deploy -c stack-compose.yml ${deploy_stack_name}
fi