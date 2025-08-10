import pathlib

import pydantic
import pydantic_settings

from brigid.core.settings import BaseSettings


def _default_static_extensions() -> dict[str, str]:
    return {
        "css": "text/css",
        "js": "application/javascript",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "svg": "image/svg+xml",
    }


class Settings(BaseSettings):
    static_base: pathlib.Path = pathlib.Path(__file__).parent / "static"
    static_redefined: pathlib.Path | None = None
    static_extensions: dict[str, str] = pydantic.Field(default_factory=_default_static_extensions)

    templates_base: pathlib.Path = pathlib.Path(__file__).parent / "templates"
    templates_redefined: pathlib.Path | None = None

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_PLUGINS_THEME_")


settings = Settings()
