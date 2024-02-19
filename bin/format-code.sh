#!/usr/bin/bash

echo "run autoflake"

./bin/utils.sh poetry run autoflake .

echo "run isort"

./bin/utils.sh poetry run isort .

echo "run black"

./bin/utils.sh poetry run black .
