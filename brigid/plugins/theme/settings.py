import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    templates_base: pathlib.Path = pathlib.Path(__file__).parent / "templates"
    templates_redefined: pathlib.Path | None = None

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_PLUGINS_THEME_")


settings = Settings()
