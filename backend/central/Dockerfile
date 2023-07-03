FROM python:3.8-slim-buster

WORKDIR /central

COPY ./central .
COPY ./central_dev /central_dev

COPY ./docker_setup.sh /

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install /central_dev
# from compose args
ARG ENV
ENV ENV=prod
COPY ./.env.prod .env.prod
COPY ./mongo.dev.conf mongo.dev.conf

RUN ["chmod", "+x", "/docker_setup.sh"]

EXPOSE 5006
# CMD ["sh", "/docker_setup.sh", "/central", "5006"]
CMD ["flask", "--app", "/central", "run", "--host=0.0.0.0", "-p", "5006"]