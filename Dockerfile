FROM ubuntu:16.04
MAINTAINER Gyuhwan Kim <gyuhwan.a.kim@gmail.com>

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD [ "python", "run.py" ]