# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /db_service

COPY ./db_service/requirements.txt requirements.txt

# from compose args
ARG ENV 
ENV ENV=${ENV}
COPY ./.env.${ENV} .env.${ENV}

RUN apt-get update \
    && apt-get install -y ffmpeg libsm6 libxext6 \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get -qq clean

COPY ./db_service/docker_setup.sh ./docker_setup.sh
RUN ["chmod", "+x", "/db_service/docker_setup.sh"]

COPY ./db_service .

EXPOSE 5002
CMD ["sh", "/db_service/docker_setup.sh"]