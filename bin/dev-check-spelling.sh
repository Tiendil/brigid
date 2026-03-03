#!/usr/bin/bash

set -e

echo "run codespell"

./bin/utils.sh poetry run codespell --toml pyproject.toml ./brigid ./README.md
