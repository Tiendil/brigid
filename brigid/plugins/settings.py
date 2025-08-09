import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    plugins: list[str] = [
        "brigid.plugins.core.plugin:plugin",
        "brigid.plugins.i18n.plugin:plugin",
        "brigid.plugins.seo.plugin:plugin",
        "brigid.plugins.include.plugin:plugin",
        "brigid.plugins.theme.plugin:plugin",
        "brigid.plugins.photoswipe.plugin:plugin",
    ]

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_PLUGINS_")


settings = Settings()
