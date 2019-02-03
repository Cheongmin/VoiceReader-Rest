FROM alpine:3.7

ARG APP_VERSION
ENV VOICEREADER_API_VERSION $APP_VERSION

COPY ./voicereader /app/voicereader
COPY config.json /app
COPY config.production.json /app
COPY firebase-adminsdk.json /app
WORKDIR /app

RUN apk add -U --no-cache gcc build-base \
    python3-dev libffi-dev openssl-dev \
    && pip3 install -r voicereader/requirements.txt

EXPOSE 5000

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "voicereader.application:create()" ]
