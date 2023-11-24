FROM python:3.8-slim-buster

WORKDIR /xai_service/pytorch_cam
COPY ./backend/xai_service/pytorch_cam .
COPY ./backend/central_dev /central_dev

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    apt-get install -y ffmpeg libsm6 libxext6 &&\
    rm -rf /var/lib/apt/lists/*
    
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install /central_dev

EXPOSE 5003
CMD flask --app "/xai_service/pytorch_cam:create_app(cam_method='${CAM_METHOD}')" run --host=0.0.0.0 -p 5003