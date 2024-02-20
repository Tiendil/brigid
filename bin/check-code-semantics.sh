#!/usr/bin/bash

set -e

echo "run autoflake"

./bin/utils.sh poetry run autoflake --check --quiet .

echo "run flake8"

./bin/utils.sh poetry run flake8 .

echo "run mypy"

./bin/utils.sh poetry run mypy --show-traceback .
