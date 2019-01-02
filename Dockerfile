FROM alpine:3.7
MAINTAINER Gyuhwan Kim <gyuhwan.a.kim@gmail.com>

COPY . /app
WORKDIR /app

RUN apk add -U --no-cache gcc build-base \
    python3-dev libffi-dev openssl-dev \
    && pip3 install -r requirements.txt

EXPOSE 5000

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "voicereader:create_app()" ]
