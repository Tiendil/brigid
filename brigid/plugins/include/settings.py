import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    templates: pathlib.Path | None = None

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_PLUGINS_INCLUDE_")


settings = Settings()
