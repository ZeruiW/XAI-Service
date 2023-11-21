FROM python:3.8-slim-buster

WORKDIR /model_service/resnet50
COPY ./model_service/resnet50 .
COPY ./central_dev /central_dev

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*
    
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install /central_dev

EXPOSE 5001
CMD ["flask", "--app", "/model_service/resnet50", "run", "--host=0.0.0.0", "-p", "5001"]