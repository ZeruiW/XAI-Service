#!/bin/bash

pip install -r ./requirements.txt &&

conda install --file db_service/requirements.txt &&
conda install --file evaluation_service/requirements.txt &&
conda install --file model_service/requirements.txt &&
conda install --file xai_service/requirements.txt &&

pip install -r db_service/requirements.txt &&
pip install -r evaluation_service/requirements.txt &&
pip install -r model_service/requirements.txt &&
pip install -r xai_service/requirements.txt &&