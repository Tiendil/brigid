import copy
import posixpath
from typing import Any, Iterable
from urllib.parse import urlparse, urlunparse

from brigid.domain import request_context


def _base_url() -> str:
    return request_context.get("storage").get_site().url  # type: ignore


def normalize_url(url: str) -> str:

    if "://" not in url:
        raise NotImplementedError("Not full url")

    schema, tail = url.split("://")

    while "//" in tail:
        tail = tail.replace("//", "/")

    url = f"{schema}://{tail}"

    parsed_url = urlparse(url)
    normalized_path = posixpath.normpath(parsed_url.path)

    if normalized_path == ".":
        normalized_path = ""

    result = urlunparse(parsed_url._replace(path=normalized_path))

    if result[-1] == "/":
        result = result[:-1]

    return result


class UrlsBase:
    __slots__ = ("language",)

    def is_noindex(self) -> bool:
        return False

    def __init__(self, language: str) -> None:
        self.language = language

    def url(self) -> str:
        raise NotImplementedError("url")

    def file_url(self, relative_path: str) -> str:
        raise NotImplementedError("file_url")

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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.language == other.language


class UrlsRoot(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{_base_url()}/{self.language}")


class UrlsAuthor(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{_base_url()}/{self.language}/about")


class UrlsFeedsAtom(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{_base_url()}/{self.language}/feeds/atom")


class UrlsSiteMapFull(UrlsBase):
    __slots__ = ()

    def url(self) -> str:
        return normalize_url(f"{_base_url()}/sitemap.xml")


class UrlsPost(UrlsBase):
    __slots__ = ("slug",)

    def __init__(self, slug: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.slug = slug

    def url(self) -> str:
        return normalize_url(f"{_base_url()}/{self.language}/posts/{self.slug}")

    def file_url(self, relative_path: str) -> str:
        return normalize_url(f"{_base_url()}/static/posts/{self.slug}/{relative_path}")

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False

        return self.slug == other.slug


class UrlsTags(UrlsBase):
    __slots__ = ("page", "required_tags", "excluded_tags", "selected_tags", "_total_pages")

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
        self._total_pages: None | int = None

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False

        return (
            self.page == other.page
            and self.required_tags == other.required_tags
            and self.excluded_tags == other.excluded_tags
        )

    def _is_same_index(self, current_url: UrlsBase) -> bool:
        if not isinstance(current_url, UrlsTags):
            return False

        if self.required_tags != current_url.required_tags:
            return False

        if self.excluded_tags != current_url.excluded_tags:
            return False

        if self.language != current_url.language:
            return False

        return True

    def is_prev_to(self, current_url: UrlsBase) -> bool:
        return self._is_same_index(current_url) and self.page + 1 == current_url.page  # type: ignore

    def is_next_to(self, current_url: UrlsBase) -> bool:
        return self._is_same_index(current_url) and self.page - 1 == current_url.page  # type: ignore

    def _get_total_pages(self) -> int:
        storage = request_context.get("storage")  # type: ignore
        posts_per_page = storage.get_site().posts_per_page  # type: ignore

        all_pages = storage.get_posts(
            language=self.language,
            require_tags=self.required_tags,
            exclude_tags=self.excluded_tags,
        )

        return (len(all_pages) + posts_per_page - 1) // posts_per_page

    @property
    def total_pages(self) -> int:
        if self._total_pages is not None:
            return self._total_pages

        self._total_pages = self._get_total_pages()

        return self._total_pages

    def is_noindex(self) -> bool:
        # we do not want crawlers to index pages with filters
        # because there are infinite number of them
        return bool(self.selected_tags)

    def url(self) -> str:
        tags = list(self.required_tags | self.excluded_tags)

        tags.sort()

        tags = [tag if tag in self.required_tags else f"-{tag}" for tag in tags]

        if self.page != 1:
            tags.append(str(self.page))

        if not tags:
            return normalize_url(f"{_base_url()}/{self.language}")

        tags_path = "/".join(tags)

        return normalize_url(f"{_base_url()}/{self.language}/tags/{tags_path}")

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

        if new_page < 1 or new_page > self.total_pages:
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
