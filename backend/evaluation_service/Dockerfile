FROM python:3.8-slim-buster

WORKDIR /evaluation_service

COPY ./evaluation_service/requirements.txt requirements.txt

RUN apt-get update \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get -qq clean
    
COPY .//evaluation_service .

EXPOSE 5004

CMD [ "flask", "--app", ".", "run", "--host=0.0.0.0", "-p", "5004"]