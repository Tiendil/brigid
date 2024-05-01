import pathlib

import pydantic
import pydantic_settings

from brigid.core.settings import BaseSettings


class PhotoSwipe(pydantic.BaseModel):
    stylesheet: str = "https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.4.2/photoswipe.min.css"
    lightbox: str = "https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.4.2/photoswipe-lightbox.esm.min.js"
    pswp: str = "https://cdnjs.cloudflare.com/ajax/libs/photoswipe/5.4.2/photoswipe.esm.min.js"


class Templates(pydantic.BaseModel):
    directory: pathlib.Path = pathlib.Path(__file__).parent / "templates"
    reload: bool = False


class Settings(BaseSettings):
    photoswipe: PhotoSwipe = PhotoSwipe()

    templates: Templates = Templates()

    model_config = pydantic_settings.SettingsConfigDict(env_prefix="BRIGID_THEME_")


settings = Settings()
