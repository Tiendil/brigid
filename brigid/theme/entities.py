import datetime
import enum

from brigid.core.entities import BaseEntity


# TODO: template names should have prefixes
class Template(enum.StrEnum):
    article_page = "article.html.j2"
    index_page = "blog_index.html.j2"


class MetaInfo(BaseEntity):
    site_title: str

    language: str
    allowed_languages: list[str]

    title: str
    seo_description: str
    author: str
    tags: list[str]
    published_at: datetime.datetime | None

    seo_image_url: str | None
