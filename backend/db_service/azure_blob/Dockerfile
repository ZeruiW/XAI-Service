FROM python:3.8-slim-buster

WORKDIR /db_service/azure_blob
COPY ./db_service/azure_blob .
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

RUN ["chmod", "+x", "/docker_setup.sh"]

EXPOSE 5007
CMD ["sh", "/docker_setup.sh", "/db_service/azure_blob", "5009"]