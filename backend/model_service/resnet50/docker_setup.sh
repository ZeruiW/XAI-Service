#!/bin/bash

if [ "$ENV" = "prod" ]; then
    echo "prod"
    flask --app . run --host=0.0.0.0 -p 5001
else
    echo "dev"
    export MYSQL_HOST=host.docker.internal
    flask --app . --debug run --host=0.0.0.0 -p 5001
fi;