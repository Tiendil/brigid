import functools
import pathlib
from typing import Iterable

from brigid.library.entities import Article, Collection, Page, Redirects, Site


class Storage:
    __slots__ = (
        "_pages",
        "_articles",
        "_articles_by_path",
        "_articles_by_slug",
        "_site",
        "_redirects",
        "_collections",
    )

    def __init__(self) -> None:
        self._pages: dict[str, Page] = {}
        self._articles: dict[str, Article] = {}
        self._collections: dict[str, Collection] = {}

        self._articles_by_path: dict[pathlib.Path, str] = {}
        self._articles_by_slug: dict[str, str] = {}

        self._site: Site | None = None
        self._redirects: Redirects | None = None

    def get_article(
        self,
        id: str | None = None,
        path: pathlib.Path | None = None,
        slug: str | None = None,
    ) -> Article:

        if sum(1 for x in (id, path, slug) if x is not None) != 1:
            raise NotImplementedError("id, path and slug are mutually exclusive")

        if id is not None:
            return self._articles[id]

        if path is not None:
            return self._articles[self._articles_by_path[path]]

        if slug is not None:
            return self._articles[self._articles_by_slug[slug]]

        raise NotImplementedError("One of id, path or slug must be provided")

    def has_article(
        self,
        id: str | None = None,
        path: pathlib.Path | None = None,
        slug: str | None = None,
    ) -> bool:

        if sum(1 for x in (id, path, slug) if x is not None) != 1:
            raise NotImplementedError("id, path and slug are mutually exclusive")

        if id is not None:
            return id in self._articles

        if path is not None:
            return path in self._articles_by_path

        if slug is not None:
            return slug in self._articles_by_slug

        raise NotImplementedError("One of id, path or slug must be provided")

    def add_article(self, article: Article, replace: bool = False) -> None:
        if not replace and article.id in self._articles:
            raise NotImplementedError("article with id already exists")

        self._articles[article.id] = article
        self._articles_by_path[article.path] = article.id
        self._articles_by_slug[article.slug] = article.id

    def add_page(self, page: Page, replace: bool = False) -> None:
        if page.article_id not in self._articles:
            raise NotImplementedError("article must be added first")

        article = self.get_article(id=page.article_id)

        if not replace and page.language in article.pages:
            raise NotImplementedError("page with language already exists")

        if not replace and page.id in article.pages.values():
            raise NotImplementedError("page with id already exists")

        article.pages[page.language] = page.id

        self._pages[page.id] = page

    def get_page(self, id: str) -> Page:
        return self._pages[id]

    def set_site(self, site: Site) -> None:
        self._site = site

    def get_site(self) -> Site:
        assert self._site
        return self._site

    def set_redirects(self, redirects: Redirects) -> None:
        self._redirects = redirects

    def get_redirects(self) -> Redirects:
        assert self._redirects
        return self._redirects

    def add_collection(self, collection: Collection) -> None:
        if collection.id in self._collections:
            raise NotImplementedError("collection already added")

        self._collections[collection.id] = collection

    def get_collection(self, id: str) -> Collection:
        return self._collections[id]

    def get_pages(self, language: str) -> list[Page]:
        return [page for page in self._pages.values() if page.language == language and not page.is_post]

    def get_posts(
        self,
        language: str,
        require_tags: Iterable[str] = (),
        exclude_tags: Iterable[str] = (),
    ) -> list[Page]:
        # fixed order of arguments for better cache performance

        required = tuple(sorted(require_tags))
        excluded = tuple(sorted(exclude_tags))

        return self._get_posts(language, required, excluded)

    @functools.lru_cache(maxsize=128)
    def _get_posts(
        self,
        language: str,
        require_tags: Iterable[str] = (),
        exclude_tags: Iterable[str] = (),
    ) -> list[Page]:
        pages = [page for page in self._pages.values() if page.language == language and page.is_post]

        if require_tags:
            require_tags = set(require_tags)
            pages = [page for page in pages if page.tags >= require_tags]

        if exclude_tags:
            exclude_tags = set(exclude_tags)
            pages = [page for page in pages if not page.tags & exclude_tags]

        pages.sort(key=lambda x: x.published_at, reverse=True)

        return pages

    def all_entities(self):
        return list(self._pages.values())


storage = Storage()
