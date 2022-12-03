FROM python:3.8-slim-buster

WORKDIR /xai_service

COPY ./xai_service/requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y ffmpeg libsm6 libxext6 \
    && python -m pip install --upgrade pip \
    
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get -qq clean
    
COPY ./xai_service .

# from compose args
ARG ENV 
ENV ENV=${ENV}
COPY ./.env.${ENV} .env.${ENV}

COPY ./xai_service/docker_setup.sh ./docker_setup.sh
RUN ["chmod", "+x", "/xai_service/docker_setup.sh"]

EXPOSE 5003
CMD ["sh", "/xai_service/docker_setup.sh"]