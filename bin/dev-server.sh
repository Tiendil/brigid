#!/usr/bin/bash

poetry run uvicorn brigid.application.application:app --host 0.0.0.0 --port 8000 --workers 1 --reload --reload-include "*"
