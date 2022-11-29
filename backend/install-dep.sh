#!/bin/bash

pip install -r ./requirements.txt &&

pip install -r db_service/requirements.txt &&
pip install -r evaluation_service/requirements.txt &&
pip install -r model_service/requirements.txt &&
pip install -r xai_service/requirements.txt
