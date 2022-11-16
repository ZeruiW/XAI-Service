# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /db_service

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y ffmpeg libsm6 libxext6 \
    && python -m pip install --upgrade pip \
    
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get -qq clean

COPY . .

EXPOSE 5002

CMD [ "flask", "--app", ".", "run", "--host=0.0.0.0", "-p", "5002"]