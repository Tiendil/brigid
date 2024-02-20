import copy
import posixpath
from typing import Any, Iterable
from urllib.parse import urlparse, urlunparse


def base_url() -> str:
    from brigid.library.storage import storage

    site = storage.get_site()
    return site.url


def normalize_url(url: str) -> str:

    schema, tail = url.split("://")

    while "//" in tail:
        tail = tail.replace("//", "/")

    url = f"{schema}://{tail}"

    parsed_url = urlparse(url)
    normalized_path = posixpath.normpath(parsed_url.path)
    return urlunparse(parsed_url._replace(path=normalized_path))


class UrlsBase:
    __slots__ = ("language",)

    is_nofollow = False

    def __init__(self, language: str) -> None:
        self.language = language

    def url(self) -> str:
        raise NotImplementedError("url")

    def file_url(self, relative_path: str) -> str:
        raise ValueError("file_url")

    def to_root(self) -> "UrlsRoot":
        return UrlsRoot(language=self.language)

    def to_feeds_atom(self) -> "UrlsFeedsAtom":
        return UrlsFeedsAtom(language=self.language)

    def to_author(self) -> "UrlsAuthor":
        return UrlsAuthor(language=self.language)

    def to_post(self, slug: str) -> "UrlsPost":
        return UrlsPost(language=self.language, slug=slug)

    def to_filter(self, page: int = 1, require: Iterable[str] = (), exclude: Iterable[str] = ()) -> "UrlsTags":
        return UrlsTags(
            language=self.language,
            page=page,
            required_tags=require,
            excluded_tags=exclude,
        )

    def to_language(self, language: str) -> Any:
        new_urls = copy.deepcopy(self)
        new_urls.language = language
        return new_urls

    def to_site_map_full(self) -> "UrlsSiteMapFull":
        return UrlsSiteMapFull(language=self.language)


class UrlsRoot(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{base_url()}/{self.language}")


class UrlsAuthor(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{base_url()}/{self.language}/about")


class UrlsFeedsAtom(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{base_url()}/{self.language}/feeds/atom")


class UrlsSiteMapFull(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{base_url()}/sitemap.xml")


class UrlsPost(UrlsBase):
    __slots__ = ("slug",)

    def __init__(self, slug: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.slug = slug

    def url(self) -> str:
        return normalize_url(f"{base_url()}/{self.language}/posts/{self.slug}")

    def file_url(self, relative_path: str) -> str:
        return normalize_url(f"{base_url()}/static/posts/{self.slug}/{relative_path}")


class UrlsTags(UrlsBase):
    __slots__ = ("page", "required_tags", "excluded_tags", "selected_tags")

    def __init__(
        self,
        page: int,
        required_tags: Iterable[str],
        excluded_tags: Iterable[str],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.page = page
        self.required_tags = frozenset(required_tags)
        self.excluded_tags = frozenset(excluded_tags)
        self.selected_tags = self.required_tags | self.excluded_tags

    # TODO: cache
    @property
    def total_pages(self) -> int:
        from brigid.library.storage import storage

        site = storage.get_site()

        all_pages = storage.last_pages(
            language=self.language,
            require_tags=self.required_tags,
            exclude_tags=self.excluded_tags,
        )
        total_pages = (len(all_pages) + site.posts_per_page - 1) // site.posts_per_page
        return total_pages

    @property
    def is_nofollow(self) -> bool:
        # we do not want crawlers to index pages with filters
        # because there are infinite number of them
        return bool(self.selected_tags)

    @is_nofollow.setter
    def is_nofollow(self, value: str) -> None:
        raise AttributeError("attribute is read-only")

    def url(self) -> str:
        tags = list(self.required_tags | self.excluded_tags)

        tags.sort()

        tags = [tag if tag in self.required_tags else f"-{tag}" for tag in tags]

        if self.page != 1:
            tags.append(str(self.page))

        if not tags:
            return normalize_url(f"{base_url()}/{self.language}")

        tags_path = "/".join(tags)

        return normalize_url(f"{base_url()}/{self.language}/tags/{tags_path}")

    def first_page(self) -> "UrlsTags":
        return UrlsTags(
            language=self.language,
            page=1,
            required_tags=self.required_tags,
            excluded_tags=self.excluded_tags,
        )

    def last_page(self) -> "UrlsTags":
        return UrlsTags(
            language=self.language,
            page=self.total_pages,
            required_tags=self.required_tags,
            excluded_tags=self.excluded_tags,
        )

    def move_page(self, delta: int) -> "UrlsTags":
        new_page = self.page + delta

        if self.page < 1 or self.page > self.total_pages:
            raise NotImplementedError("Wrong page number")

        return UrlsTags(
            language=self.language,
            page=new_page,
            required_tags=self.required_tags,
            excluded_tags=self.excluded_tags,
        )

    def require(self, *tags: str) -> "UrlsTags":
        return UrlsTags(
            language=self.language,
            page=1,
            required_tags=self.required_tags | set(tags),
            excluded_tags=self.excluded_tags - set(tags),
        )

    def exclude(self, *tags: str) -> "UrlsTags":
        return UrlsTags(
            language=self.language,
            page=1,
            required_tags=self.required_tags - set(tags),
            excluded_tags=self.excluded_tags | set(tags),
        )

    def remove(self, *tags: str) -> "UrlsTags":
        return UrlsTags(
            language=self.language,
            page=1,
            required_tags=self.required_tags - set(tags),
            excluded_tags=self.excluded_tags - set(tags),
        )
