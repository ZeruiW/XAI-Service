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

docker compose up --build &&



# Check path
echo "Checking paths..."
flask --app db_service routes
flask --app model_service/resnet50 routes
flask --app xai_service/pytorch_cam routes

# Run server in debug
flask --app model_service/resnet50 --debug run -p 5001 &
flask --app db_service --debug run -p 5002 &
flask --app xai_service/pytorch_cam --debug run -p 5003 &
flask --app evaluation_service --debug run -p 5004