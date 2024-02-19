#!/usr/bin/bash

set -e

echo "run isort"

./bin/utils.sh poetry run isort --check-only .

echo "run black"

./bin/utils.sh poetry run black --check .
