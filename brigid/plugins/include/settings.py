import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings
from brigid.library.settings import settings as library_settings


class Settings(BaseSettings):
    templates: pathlib.Path = library_settings.directory / "plugins" / "include" / "templates"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_PLUGINS_INCLUDE_")


settings = Settings()
