

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    reload_templates: bool = False

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_THEME_")


settings = Settings()
