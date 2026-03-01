FROM python:3.12

RUN pip install poetry

ARG UID=1000
ARG GID=1000
ARG USER=brigid

RUN groupadd --gid $GID $USER && useradd --create-home --uid $UID --gid $USER --shell /bin/bash $USER

WORKDIR /repository

# copied code will be replaced by mounted volume in docker-compose
# but we need to copy it to install cli utils from pyproject.toml
COPY --chown=$USER:$USER ./ ./

USER $USER

RUN poetry install --with dev --no-interaction --no-ansi

USER $USER
CMD []
