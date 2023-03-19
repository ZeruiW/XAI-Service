# FROM python:3.8-slim-buster

# WORKDIR /model_service/resnet50
# COPY ./model_service/resnet50 .
# COPY ./central_dev /central_dev
# COPY ./docker_setup.sh /

# RUN apt-get update && \
#     apt-get -y install gcc mono-mcs && \
#     rm -rf /var/lib/apt/lists/*
    
# RUN python -m pip install --upgrade pip \
#     && pip install -r requirements.txt

# RUN pip install /central_dev

# # from compose args
# ARG ENV 
# ENV ENV=${ENV}
# COPY ./.env.${ENV} .env.${ENV}

# RUN ["chmod", "+x", "/docker_setup.sh"]

# EXPOSE 5001
# CMD ["sh", "/docker_setup.sh", "/model_service/resnet50", "5001"]