FROM python:3.8-slim-buster

WORKDIR /model_service/ACSCV
COPY ./model_service/ACSCV .
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

EXPOSE 5001
CMD ["sh", "/docker_setup.sh", "/model_service/resnet50", "5001"]