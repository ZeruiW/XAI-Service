FROM python:3.8-slim-buster

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /central

COPY ./central .


RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./central_dev /central_dev
RUN pip install /central_dev

EXPOSE 5006
CMD ["flask", "--app", "/central", "run", "--host=0.0.0.0", "-p", "5006"]