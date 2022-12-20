FROM python:3.8-slim-buster

WORKDIR /model_service/azure_cog
COPY ./model_service/azure_cog .
COPY ./central_dev /central_dev
COPY ./docker_setup.sh /

RUN pip install /central_dev

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt


# from compose args
ARG ENV 
ENV ENV=${ENV}
COPY ./.env.${ENV} .env.${ENV}

RUN ["chmod", "+x", "/docker_setup.sh"]

EXPOSE 5007
CMD ["sh", "/docker_setup.sh", "/model_service/azure_cog", "5007"]