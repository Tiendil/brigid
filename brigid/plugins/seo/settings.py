import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    templates: pathlib.Path = pathlib.Path(__file__).parent / "templates"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_PLUGINS_SEO_")


settings = Settings()
