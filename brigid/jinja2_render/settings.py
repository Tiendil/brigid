import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    templates_reload: bool = False

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_JINJA2_RENDER_")


settings = Settings()
