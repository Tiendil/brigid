#!/usr/bin/bash

set -e

CONTAINER="brigid:check-runnable-in-prod"

echo "build container"

docker build -t $CONTAINER -f ./docker/Dockerfile .

echo "run checks"

echo "check that CLI works"
docker run --rm $CONTAINER brigid --help

echo "check that CLI shows configs"
docker run --rm $CONTAINER brigid print-configs
