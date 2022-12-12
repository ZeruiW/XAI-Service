FROM python:3.8-slim-buster

WORKDIR /model_service/resnet50

COPY ./model_service/resnet50/requirements.txt requirements.txt

COPY ./central_dev /central_dev

RUN pip install /central_dev

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./model_service/resnet50 .

# from compose args
ARG ENV 
ENV ENV=${ENV}
COPY ./.env.${ENV} .env.${ENV}

RUN ["chmod", "+x", "/model_service/resnet50/docker_setup.sh"]

EXPOSE 5001
CMD ["sh", "/model_service/resnet50/docker_setup.sh"]