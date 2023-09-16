FROM python:3.8-slim-buster

WORKDIR /evaluation_service

COPY ./evaluation_service .
COPY ./central_dev /central_dev
COPY ./docker_setup.sh /

RUN apt-get update \
    && apt-get install -y libgl1-mesa-glx \
    && apt-get -y install gcc mono-mcs \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get -qq clean

RUN pip install /central_dev
# from compose args
ARG ENV
ENV ENV=${ENV}
COPY ./.env.prod .env.prod
COPY ./mongo.dev.conf mongo.dev.conf

RUN ["chmod", "+x", "/docker_setup.sh"]

EXPOSE 5004
CMD ["flask", "--app", "/evaluation_service", "run", "--host=0.0.0.0", "-p", "5004"]
#CMD ["sh", "/docker_setup.sh", "/evaluation_service", "5004"]