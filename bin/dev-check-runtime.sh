#!/usr/bin/bash

set -e

echo "check that CLI works"
./bin/utils.sh poetry run brigid --help

echo "check that CLI shows configs"
./bin/utils.sh poetry run brigid print-configs
