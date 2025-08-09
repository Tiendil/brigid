import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    templates: pathlib.Path = pathlib.Path(__file__).parent / "templates"
    templates_reload: bool = False

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_THEME_")


settings = Settings()
