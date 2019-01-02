#FROM python:3.7.2-alpine3.7 as base
#
#FROM base as builder
#
#RUN mkdir /install
#WORKDIR /install
#
#COPY requirements.txt /requirements.txt
#
#RUN apk add -U --no-cache gcc build-base linux-headers \
#    ca-certificates python3-dev libffi-dev
#RUN pip install -r /requirements.txt
#
#FROM base
#
#COPY --from=builder /install /usr/local
#COPY . /app
#
#WORKDIR /app
#
#CMD [ "python", "run.py" ]
FROM alpine:3.7
MAINTAINER Gyuhwan Kim <gyuhwan.a.kim@gmail.com>

COPY . /app
WORKDIR /app

RUN apk add -U --no-cache gcc build-base \
    python3-dev libffi-dev openssl-dev \
    && pip3 install -r requirements.txt

EXPOSE 5000

CMD [ "python3", "run.py" ]
