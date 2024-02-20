import datetime
import enum
import pathlib
import re
from typing import Literal

import pydantic

from brigid.core.entities import BaseEntity
from brigid.domain import urls

MORE_RE = re.compile(r"<!--\s*more\s*-->", re.IGNORECASE)


class MenuItemType(enum.StrEnum):
    article = "article"
    feed = "feed"
    external = "external"
    blog = "blog"


class ArticleType(enum.StrEnum):
    post = "post"
    page = "page"


class OrderDirection(enum.StrEnum):
    asc = "asc"
    desc = "desc"


class MenuItemBase(BaseEntity):
    name: str
    language: str | None = None

    model_config = pydantic.ConfigDict(frozen=False)

    def is_active(self, current_slug: str) -> bool:
        return False


class MenuItemArticle(MenuItemBase):
    type: Literal[MenuItemType.article]
    slug: str

    def is_active(self, current_slug: str) -> bool:
        return self.slug == current_slug

    @property
    def url(self) -> str:
        return urls.UrlsPost(language=self.language, slug=self.slug).url()


class MenuItemFeed(MenuItemBase):
    type: Literal[MenuItemType.feed]

    @property
    def url(self) -> str:
        assert self.language is not None
        return urls.UrlsFeedsAtom(language=self.language).url()


class MenuItemExternal(MenuItemBase):
    type: Literal[MenuItemType.external]
    url: str


class MenuItemBlog(MenuItemBase):
    type: Literal[MenuItemType.blog]

    def is_active(self, current_slug: str) -> bool:
        return current_slug is None

    @property
    def url(self) -> str:
        assert self.language is not None
        return urls.UrlsRoot(language=self.language).url()


MenuItem = MenuItemArticle | MenuItemFeed | MenuItemExternal | MenuItemBlog


class SimilarityConfig(BaseEntity):
    common_tag_score: int = 100
    referenced_from_score: int = 100
    referenced_to_score: int = 100
    bonus_per_reference: int = 10
    ignore_similar_tags: set[str] = pydantic.Field(default_factory=set)
    bonus_for_tags: dict[str, int] = pydantic.Field(default_factory=dict)


class SiteLanguage(BaseEntity):
    title: str
    subtitle: str
    author: str

    tags_translations: dict[str, str] = pydantic.Field(default_factory=dict)
    theme_translations: dict[str, str] = pydantic.Field(default_factory=dict)
    seo_translations: dict[str, str] = pydantic.Field(default_factory=dict)

    menu: list[MenuItem] = pydantic.Field(default_factory=list)


class Site(BaseEntity):
    url: str  # TODO: pydantic.UrlStr

    default_language: str
    allowed_languages: set[str] = pydantic.Field(default_factory=set)
    posts_per_page: int = 5
    posts_in_feed: int = 10
    posts_in_latest: int = 20
    posts_in_similar: int = 6
    languages: dict[str, SiteLanguage] = pydantic.Field(default_factory=dict)
    default_page_template: str = "article.html.j2"
    favicon: str | None = None

    path: pathlib.Path

    footer_html: str | None = None
    header_html: str | None = None

    similarity: SimilarityConfig = SimilarityConfig()

    model_config = pydantic.ConfigDict(frozen=False)


class Article(BaseEntity):
    path: pathlib.Path

    slug: str

    type: ArticleType = ArticleType.post

    title: str | None = None

    pages: dict[str, str] = pydantic.Field(default_factory=dict)

    feed: bool = False

    tags: set[str] = pydantic.Field(default_factory=list)

    @property
    def more_than_one_language(self) -> bool:
        return len(self.pages) > 1

    @property
    def id(self) -> str:
        return f"article#{self.slug}"


class Page(BaseEntity):
    article_id: str

    path: pathlib.Path

    # TODO: if in the future, than we hide the article?
    published_at: datetime.datetime

    language: str

    title: str

    # Google could show max from 155 to 160 characters from description in the search results
    # Facebook, Twitter could show more characters
    # But we'll stick to minimum from maximum
    description: str = pydantic.Field(max_length=155)

    # could be None, but page should define it explicitly
    seo_image: str | None

    body: str

    tags: set[str] = pydantic.Field(default_factory=list)

    template: str | None = None

    @property
    def id(self) -> str:
        return f"page#{self.language}#{self.slug}"

    @property
    def slug(self) -> str:
        from brigid.library.storage import storage

        return storage.get_article(id=self.article_id).slug

    @property
    def is_post(self) -> bool:
        from brigid.library.storage import storage

        return storage.get_article(id=self.article_id).type == ArticleType.post

    @property
    def has_more(self) -> bool:
        return MORE_RE.search(self.body) is not None

    @property
    def intro(self) -> str:
        if not self.has_more:
            return self.body

        return MORE_RE.split(self.body)[0]

    @property
    def tags_in_translation_order(self) -> list[str]:
        from brigid.library.storage import storage

        translations = storage.get_site().languages[self.language].tags_translations

        tags = list(self.tags)
        tags.sort(key=lambda tag: translations[tag])

        return tags


class PageSimilarityScore(BaseEntity):
    page_id: str
    score: int

    explanations: list[str] = pydantic.Field(default_factory=list)

    model_config = pydantic.ConfigDict(frozen=False)

    def add_score(self, score: int, explanation: str) -> None:
        self.score += score
        self.explanations.append(f"{score}: {explanation}")


class Redirects(BaseEntity):
    permanent: dict[str, str] = pydantic.Field(default_factory=dict)


class Collection(BaseEntity):
    id: str
    path: pathlib.Path

    required_tags: set[str] = pydantic.Field(default_factory=set)
    excluded_tags: set[str] = pydantic.Field(default_factory=set)

    order: OrderDirection = OrderDirection.asc

    css_for_tags: dict[str, str] = pydantic.Field(default_factory=dict)

    def classes_for_tags(self, tags: set[str]) -> list[str]:
        classes = []

        for tag in tags:
            if tag in self.css_for_tags:
                classes.append(self.css_for_tags[tag])

        return classes
