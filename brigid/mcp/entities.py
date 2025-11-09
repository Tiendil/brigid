
import datetime
import pydantic
from brigid.core.entities import BaseEntity
from brigid.library.entities import ArticleType


class PageInfo(BaseEntity):
    published_at: datetime.datetime
    language: str
    slug: str
    title: str
    seo_description: str = pydantic.Field(max_length=155)
    seo_image: str | None
    tags: set[str] = pydantic.Field(default_factory=set)
    series: str | None = None
    type: ArticleType
    intro: str
    has_more: bool
