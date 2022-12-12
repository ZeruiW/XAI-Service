FROM python:3.8-slim-buster

WORKDIR /central

COPY ./central/requirements.txt requirements.txt

COPY ./central_dev /central_dev

RUN pip install /central_dev

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./central .

# from compose args
ARG ENV 
ENV ENV=${ENV}
COPY ./.env.${ENV} .env.${ENV}

RUN ["chmod", "+x", "/central/docker_setup.sh"]

EXPOSE 5006
CMD ["sh", "/central/docker_setup.sh"]