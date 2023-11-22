#!/bin/bash

if [ "$ENV" = "prod" ]; then
    echo "prod"
    flask --app $1 run --host=0.0.0.0 -p $2
else
    echo "dev"
    flask --app $1 --debug run --host=0.0.0.0 -p $2
fi;