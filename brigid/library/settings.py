import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    directory: pathlib.Path = pathlib.Path.cwd() / "content"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_LIBRARY_")


settings = Settings()
