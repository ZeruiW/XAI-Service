FROM python:3.8-slim-buster

WORKDIR /evaluation_service
COPY ./evaluation_service .
COPY ./central_dev /central_dev

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    apt-get install -y ffmpeg libsm6 libxext6 &&\
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install /central_dev


EXPOSE 5004
CMD ["flask", "--app", "/evaluation_service", "run", "--host=0.0.0.0", "-p", "5004"]