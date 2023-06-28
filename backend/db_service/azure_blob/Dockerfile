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
RUN pip install prometheus_client

# from compose args
ARG ENV
ENV ENV=prod
COPY ./.env.prod .env.prod

RUN ["chmod", "+x", "/docker_setup.sh"]

EXPOSE 5009
#CMD ["sh", "/docker_setup.sh", "/db_service/azure_blob", "5009"]
CMD ["flask", "--app", "/db_service/azure_blob", "run", "--host=0.0.0.0", "-p", "5009"]