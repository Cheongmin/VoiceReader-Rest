#!/usr/bin/env bash
# Require envvars
# DOCKER_USERNAME
# DOCKER_IMAGE_NAME

if [[ -z $1 ]]; then
    echo "Can't get version"
    exit 1
fi

APP_VERSION=$1

echo ${APP_VERSION} > VERSION

docker build -t ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${APP_VERSION} .
docker tag ${DOCKER_USERNAME}/${DOCKER_IMAGE_NAME}:${APP_VERSION} ${DOCKER_IMAGE_NAME}:latest