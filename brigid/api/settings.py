import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    cache_directory: pathlib.Path | None = None

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_API_")


settings = Settings()
