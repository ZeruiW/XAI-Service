FROM python:3.8-slim-buster

WORKDIR /xai_service/pytorch_cam

COPY ./xai_service/pytorch_cam .
COPY ./central_dev /central_dev
COPY ./docker_setup.sh /

RUN apt-get update && \
    apt-get -y install gcc mono-mcs \
    && apt-get install -y ffmpeg libsm6 libxext6 \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get -qq clean


RUN pip install /central_dev
RUN pip install grad-cam GPUtil
# RUN python -m pip install --upgrade pip \
#     && pip install -r requirements.txt

# from compose args
ARG ENV
ENV ENV=prod
COPY ./.env.prod .env.prod
COPY ./mongo.dev.conf mongo.dev.conf

ENV CAM_METHOD=grad-cam

RUN ["chmod", "+x", "/docker_setup.sh"]

EXPOSE 5003
CMD ["flask", "--app", "/xai_service/pytorch_cam:create_app(cam_method='grad-cam')", "run", "--host=0.0.0.0", "-p", "5003"]
# CMD ["/docker_setup.sh", "xai_service/pytorch_cam:create_app(cam_method="$CAM_METHOD")", "5003"]