#!/usr/bin/bash

set -e

echo "run tests"

./bin/utils.sh poetry run pytest brigid
