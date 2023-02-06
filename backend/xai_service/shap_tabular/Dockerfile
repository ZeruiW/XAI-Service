# FROM python:3.8-slim-buster

# WORKDIR /xai_service/shap_tabular

# COPY ./xai_service/shap_tabular .
# COPY ./central_dev /central_dev
# COPY ./docker_setup.sh /

# RUN pip install /central_dev

# RUN apt-get update \
#     && apt-get install -y ffmpeg libsm6 libxext6 \
#     && python -m pip install --upgrade pip \
    
#     && pip install -r requirements.txt \
#     && rm -rf /var/lib/apt/lists/* \
#     && apt-get -qq autoremove \
#     && apt-get -qq clean

# # RUN python -m pip install --upgrade pip \
# #     && pip install -r requirements.txt

# # from compose args
# ARG ENV 
# ENV ENV=${ENV}
# COPY ./.env.${ENV} .env.${ENV}

# RUN ["chmod", "+x", "/docker_setup.sh"]

# EXPOSE 5012
# CMD ["sh", "/docker_setup.sh", "/xai_service/shap_tabular", "5012"]