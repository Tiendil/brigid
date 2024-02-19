import datetime
import pathlib

import pydantic
import pydantic_settings
from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    directory: pathlib.Path

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_LIBRARY_")


settings = Settings()
