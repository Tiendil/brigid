import datetime
import pathlib
import uuid
from typing import Iterable

from brigid.core.utils import now
from brigid.library.entities import Article, ArticleType, Page
from brigid.library.storage import storage


def article(
    path: pathlib.Path | None = None, slug: str | None = None, type: ArticleType = ArticleType.post
) -> Article:

    if path is None:
        path = pathlib.Path("/tmp/brigid/tests") / uuid.uuid4().hex / "article.toml"  # noqa: S108

    if slug is None:
        slug = uuid.uuid4().hex

    article = Article(path=path, slug=slug, type=type, pages={}, tags=set())

    storage.add_article(article)

    return article


_article = article


def page(  # noqa: CFQ002
    article: Article | None = None,
    path: pathlib.Path | None = None,
    published_at: datetime.datetime | None = None,
    language: str = "en",
    title: str | None = None,
    seo_description: str | None = None,
    seo_image: str | None = None,
    body: str | None = None,
    tags: Iterable[str] = (),
    template: str | None = None,
) -> Page:

    if article is None:
        article = _article()

    if path is None:
        path = article.path.parent / f"{language}.md"

    if title is None:
        title = f"Title: {article.slug} {language}"

    if seo_description is None:
        seo_description = f"Description: {article.slug} {language}"

    if published_at is None:
        published_at = now()

    if body is None:
        body = f"Body: {article.slug} {language}"

    page = Page(
        article_id=article.id,
        path=path,
        published_at=published_at,
        language=language,
        title=title,
        seo_description=seo_description,
        seo_image=seo_image,
        body=body,
        tags=set(tags),
        template=template,
    )

    storage.add_page(page)

    return page
