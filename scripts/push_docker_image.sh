#!/usr/bin/env bash
# Require envvars
# DOCKER_USERNAME
# DOCKER_PASSWORD
# DOCKER_IMAGE_NAME

if [[ -z $1 ]]; then
    echo "Can't get tag of image"
    exit 1
fi

IMAGE_TAG=$1

docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
if [[ $? != 0 ]]; then
    echo "Can't dockerhub login"
    exit 2
fi

docker push ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${IMAGE_TAG}
docker push ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:latest