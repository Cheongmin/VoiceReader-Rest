#!/usr/bin/env bash
# Using script on Travis CI


# Create VERSION file for application versioning
echo ${TRAVIS_TAG} > VERSION

# Image build and deploy to Dockerhub
bash scripts/dockerhub-deploy.sh

# App deploy to AWS EC2 with fabric
fab -f scripts/ec2-deploy.py deploy
