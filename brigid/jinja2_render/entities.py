import datetime
import enum

import pydantic

from brigid.core.entities import BaseEntity
from brigid.domain.urls import UrlsBase
from brigid.library.entities import Article, Page, PageSimilarityScore


# TODO: template names should have prefixes
class Template(enum.StrEnum):
    article_page = "theme/article.html.j2"
    index_page = "theme/blog_index.html.j2"


class Info(BaseEntity):
    language: str
    current_url: UrlsBase

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
    )


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


class IndexInfo(BaseEntity):
    pages: list[Page]
    pages_found: int
    tags_count: dict[str, int]


class PageInfo(BaseEntity):
    article: Article
    page: Page
    similar_pages: list[PageSimilarityScore]
