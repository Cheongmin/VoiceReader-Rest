docker login -u ${DOCKER_USERNAME} --password-stdin ${DOCKER_PASSWORD}

docker build -t gyuhwankim/voicereader-rest:0.0.1 .
docker tag gyuhwankim/voicereader-rest:0.0.1 gyuhwankim/voicereader-rest:latest

docker push gyuhwankim/voicereader-rest:0.0.1
docker push gyuhwankim/voicereader-rest:latest