import datetime

from brigid.core.entities import BaseEntity


class MetaInfo(BaseEntity):
    language: str
    allowed_languages: list[str]

    title: str
    description: str
    author: str
    tags: list[str]
    published_at: datetime.datetime | None

    seo_image_url: str | None
