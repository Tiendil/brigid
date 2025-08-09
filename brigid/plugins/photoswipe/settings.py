import pathlib

import pydantic_settings

from brigid.core.settings import BaseSettings


class Settings(BaseSettings):
    templates: pathlib.Path = pathlib.Path(__file__).parent / "templates"

    stylesheet: str = "https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.4.2/photoswipe.min.css"
    lightbox: str = "https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.4.2/photoswipe-lightbox.esm.min.js"
    pswp: str = "https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.4.2/photoswipe.esm.min.js"

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_PLUGINS_PHOTOSWIPE_")


settings = Settings()
