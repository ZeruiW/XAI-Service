FROM python:3.8-slim-buster

WORKDIR /model_service/azure_cog
COPY ./model_service/azure_cog .
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
COPY ./mongo.dev.conf mongo.dev.conf

RUN ["chmod", "+x", "/docker_setup.sh"]

EXPOSE 5007
CMD ["flask", "--app", "/model_service/azure_cog", "run", "--host=0.0.0.0", "-p", "5007"]