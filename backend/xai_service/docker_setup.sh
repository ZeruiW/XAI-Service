#!/bin/bash

if [ "$ENV" = "prod" ]; then
    echo "prod"
    flask --app pytorch_cam run --host=0.0.0.0 -p 5003
else
    echo "dev"
    export MYSQL_HOST=host.docker.internal
    flask --app pytorch_cam --debug run --host=0.0.0.0 -p 5003
fi;