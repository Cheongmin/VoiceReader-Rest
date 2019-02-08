#!/usr/bin/env bash
# Using script on Travis CI

if [[ -z $1 ]]; then
    echo "Can't get version"
    exit 1
fi

TARGET_VERSION=$1

# Build docker image
bash scripts/build_docker_image.sh ${TARGET_VERSION}
if [[ $? != 0 ]]; then
    echo "Failed to build docker image."
    exit 1
fi

# Push docker image to Dockerhub
bash scripts/push_docker_image.sh ${TARGET_VERSION}
if [[ $? != 0 ]]; then
    echo "Failed to push docker image."
    exit 2
fi


## Deploy app to AWS EC2 with fabric
fab -f scripts/deploy_app.py deploy:${TARGET_VERSION}
