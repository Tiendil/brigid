import copy
from typing import Any
from unittest import mock

import pytest

from brigid.domain.urls import (
    UrlsAuthor,
    UrlsBase,
    UrlsFeedsAtom,
    UrlsMCP,
    UrlsPost,
    UrlsRoot,
    UrlsSiteMapFull,
    UrlsStatic,
    UrlsTags,
    add_base_path,
    mcp_url,
    normalize_url,
    root_url,
    strip_base_path,
)
from brigid.library.storage import storage

base_url = "http://0.0.0.0:8000"


class TestNormalizeUrl:

    @pytest.mark.parametrize("url_in", ["", "example.com", "example.com/////", "child.example.com//"])
    def test_wrong_url(self, url_in):
        with pytest.raises(NotImplementedError):
            normalize_url(url_in)

    @pytest.mark.parametrize(
        "url_in,url_out",
        [
            ("https://example.com", "https://example.com"),
            ("https://example.com/", "https://example.com"),
            ("https://example.com//", "https://example.com"),
            ("https://example.com/////", "https://example.com"),
            ("https://child.example.com//", "https://child.example.com"),
            ("https://example.com/path/b/c", "https://example.com/path/b/c"),
            ("https://example.com/path/b/c/", "https://example.com/path/b/c"),
            ("https://example.com//path///b///c", "https://example.com/path/b/c"),
            ("https://example.com/path/b/c?", "https://example.com/path/b/c"),
            ("http://example.com//path///b///c", "http://example.com/path/b/c"),
        ],
    )
    def test_normalization(self, url_in: str, url_out: str):
        assert normalize_url(url_in) == url_out


class TestStripBasePath:

    @pytest.mark.parametrize(
        "path,prefix,expected",
        [
            ("", "", ""),
            ("/", "", ""),
            ("/en", "", "en"),
            ("en", "", "en"),
            ("/blog", "/blog", ""),
            ("/blog/en", "/blog", "en"),
            ("blog/en", "/blog", "en"),
            ("/en", "/blog", "en"),
            ("/long/complex/prefix/en", "/long/complex/prefix", "en"),
        ],
    )
    def test_strip_base_path(self, path: str, prefix: str, expected: str) -> None:
        with mock.patch("brigid.domain.urls._base_path_prefix", return_value=prefix):
            assert strip_base_path(path) == expected


class TestAddBasePath:

    @pytest.mark.parametrize(
        "path,prefix,expected",
        [
            ("", "", "/"),
            ("/en", "", "/en"),
            ("en", "", "/en"),
            ("/", "/blog", "/blog"),
            ("/en", "/blog", "/blog/en"),
            ("en", "/blog", "/blog/en"),
            ("/en", "/long/complex/prefix", "/long/complex/prefix/en"),
        ],
    )
    def test_add_base_path(self, path: str, prefix: str, expected: str) -> None:
        with mock.patch("brigid.domain.urls._base_path_prefix", return_value=prefix):
            assert add_base_path(path) == expected


class _TestUrlsBase:

    base_language = "en"
    alt_language = "ru"

    @pytest.fixture
    def url(self):
        return self._consruct_url()

    def _consruct_url(self) -> Any:
        raise NotImplementedError()

    def test_base_initialized(self, url: UrlsBase) -> None:
        assert url.language == self.base_language

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert isinstance(url.url(), str)

    def test_path_method_redefined(self, url: UrlsBase) -> None:
        assert isinstance(url.path(), str)

    def test_robots_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.robots_url() == f"/{url.path()}/"

    def test_file_url(self, url: UrlsBase) -> None:
        with pytest.raises(NotImplementedError):
            url.file_url("")

    def test_to_root(self, url: UrlsBase) -> None:
        assert url.to_root() == UrlsRoot(language=self.base_language)

    def test_to_feeds_atom(self, url: UrlsBase) -> None:
        assert url.to_feeds_atom() == UrlsFeedsAtom(language=self.base_language)

    def test_to_author(self, url: UrlsBase) -> None:
        assert url.to_author() == UrlsAuthor(language=self.base_language)

    def test_to_post(self, url: UrlsBase) -> None:
        assert url.to_post("xxx") == UrlsPost(language=self.base_language, slug="xxx")

    def test_to_filter(self, url: UrlsBase) -> None:
        filter_url = url.to_filter(page=13, require=("a", "b"), exclude=("c", "d", "e"))

        expected_filter_url = UrlsTags(
            language=self.base_language,
            page=13,
            required_tags=("a", "b"),
            excluded_tags=("c", "d", "e"),
        )

        assert filter_url == expected_filter_url

    def test_language(self, url: UrlsBase) -> None:
        expected_url = copy.deepcopy(url)
        expected_url.language = self.alt_language

        assert url.to_language(self.alt_language) == expected_url

    def test_site_map_full(self, url: UrlsBase) -> None:
        assert url.to_site_map_full() == UrlsSiteMapFull(language=self.base_language)

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/favicon.ico"),
            ("https://example.com/blog", "https://example.com/blog/favicon.ico"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/favicon.ico"),
        ],
    )
    def test_to_favicon(self, url: UrlsBase, base_url: str, expected_url: str) -> None:
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.to_favicon().url() == expected_url

    def test_noindex(self, url: UrlsBase) -> None:
        assert not url.is_noindex()


class TestUrlsBase(_TestUrlsBase):

    def _consruct_url(self) -> UrlsBase:
        return UrlsBase(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        with pytest.raises(NotImplementedError):
            url.url()

    def test_path_method_redefined(self, url: UrlsBase) -> None:
        with pytest.raises(NotImplementedError):
            url.path()

    def test_robots_url_method_redefined(self, url: UrlsBase) -> None:
        with pytest.raises(NotImplementedError):
            url.robots_url()


class TestUrlsRoot(_TestUrlsBase):

    def _consruct_url(self) -> UrlsRoot:
        return UrlsRoot(language=self.base_language)

    def test_root_url_constructor(self) -> None:
        assert root_url(self.base_language) == UrlsRoot(language=self.base_language)

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en"),
            ("https://example.com/blog", "https://example.com/blog/en"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en"),
        ],
    )
    def test_url_method_redefined(self, url: UrlsBase, base_url: str, expected_url: str) -> None:
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url


class TestUrlsAuthor(_TestUrlsBase):

    def _consruct_url(self) -> UrlsAuthor:
        return UrlsAuthor(language=self.base_language)

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en/posts/about"),
            ("https://example.com/blog", "https://example.com/blog/en/posts/about"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en/posts/about"),
        ],
    )
    def test_url_method_redefined(self, url: UrlsBase, base_url: str, expected_url: str) -> None:
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url


class TestUrlsFeedsAtom(_TestUrlsBase):

    def _consruct_url(self) -> UrlsFeedsAtom:
        return UrlsFeedsAtom(language=self.base_language)

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en/feeds/atom"),
            ("https://example.com/blog", "https://example.com/blog/en/feeds/atom"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en/feeds/atom"),
        ],
    )
    def test_url_method_redefined(self, url: UrlsBase, base_url: str, expected_url: str) -> None:
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url


class TestUrlsPost(_TestUrlsBase):

    def _consruct_url(self) -> UrlsPost:
        return UrlsPost(language=self.base_language, slug="some-slug")

    def test_initialized(self, url: UrlsPost) -> None:
        assert url.slug == "some-slug"

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en/posts/some-slug"),
            ("https://example.com/blog", "https://example.com/blog/en/posts/some-slug"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en/posts/some-slug"),
        ],
    )
    def test_url_method_redefined(self, url: UrlsPost, base_url: str, expected_url: str) -> None:  # type: ignore
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url

    def test_file_url(self, url: UrlsPost) -> None:  # type: ignore
        filepath = "images/some-image.png"
        assert url.file_url(filepath) == f"{base_url}/static/posts/some-slug/{filepath}"

    @mock.patch("brigid.domain.urls._base_url", return_value="https://example.com/blog")
    def test_file_url__prefix_blog(self, _):
        assert (
            UrlsPost(language=self.base_language, slug="some-slug").file_url("images/some-image.png")
            == "https://example.com/blog/static/posts/some-slug/images/some-image.png"
        )


class TestUrlsTags(_TestUrlsBase):

    def _consruct_url(self) -> UrlsTags:
        return UrlsTags(language=self.base_language, page=13, required_tags=("a", "d"), excluded_tags=("c", "b", "e"))

    def test_initialized(self, url: UrlsTags) -> None:
        assert url.page == 13
        assert url.required_tags == {"a", "d"}
        assert url.excluded_tags == {"c", "b", "e"}
        assert url.selected_tags == {"a", "b", "c", "d", "e"}

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en/tags/a/-b/-c/d/-e/13"),
            ("https://example.com/blog", "https://example.com/blog/en/tags/a/-b/-c/d/-e/13"),
            (
                "https://example.com/long/complex/prefix",
                "https://example.com/long/complex/prefix/en/tags/a/-b/-c/d/-e/13",
            ),
        ],
    )
    def test_url_method_redefined(self, url: UrlsTags, base_url: str, expected_url: str) -> None:  # type: ignore
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en"),
            ("https://example.com/blog", "https://example.com/blog/en"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en"),
        ],
    )
    def test_url_method__empty(self, base_url: str, expected_url: str) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=(), excluded_tags=())
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en/tags/a/b"),
            ("https://example.com/blog", "https://example.com/blog/en/tags/a/b"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en/tags/a/b"),
        ],
    )
    def test_url_method__only_required(self, base_url: str, expected_url: str) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=("a", "b"), excluded_tags=())
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en/tags/-a/-b"),
            ("https://example.com/blog", "https://example.com/blog/en/tags/-a/-b"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en/tags/-a/-b"),
        ],
    )
    def test_url_method__only_excluded(self, base_url: str, expected_url: str) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=(), excluded_tags=("a", "b"))
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url

    @pytest.mark.parametrize(
        "base_url,expected_url",
        [
            ("https://example.com", "https://example.com/en/tags/13"),
            ("https://example.com/blog", "https://example.com/blog/en/tags/13"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/en/tags/13"),
        ],
    )
    def test_url_method__only_page(self, base_url: str, expected_url: str) -> None:
        url = UrlsTags(language=self.base_language, page=13, required_tags=(), excluded_tags=())
        with mock.patch("brigid.domain.urls._base_url", return_value=base_url):
            assert url.url() == expected_url

    def test_robots_url__empty(self) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=(), excluded_tags=())
        assert url.robots_url() == f"/{self.base_language}/tags/"

    @pytest.mark.parametrize(
        "path_prefix,expected_url",
        [
            ("/blog", "/blog/en/tags/"),
            ("/long/complex/prefix", "/long/complex/prefix/en/tags/"),
        ],
    )
    def test_robots_url__empty__prefixed(self, path_prefix: str, expected_url: str) -> None:
        with mock.patch("brigid.domain.urls._base_path_prefix", return_value=path_prefix):
            url = UrlsTags(language=self.base_language, page=1, required_tags=(), excluded_tags=())
            assert url.robots_url() == expected_url

    def test_robots_url__not_empty(self) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=("sample",), excluded_tags=())
        assert url.robots_url() == f"/{self.base_language}/tags/sample/"

    @pytest.mark.parametrize(
        "path_prefix,expected_url",
        [
            ("/blog", "/blog/en/tags/sample/"),
            ("/long/complex/prefix", "/long/complex/prefix/en/tags/sample/"),
        ],
    )
    def test_robots_url__not_empty__prefixed(self, path_prefix: str, expected_url: str) -> None:
        with mock.patch("brigid.domain.urls._base_path_prefix", return_value=path_prefix):
            url = UrlsTags(language=self.base_language, page=1, required_tags=("sample",), excluded_tags=())
            assert url.robots_url() == expected_url

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_is_same_index(self, url: UrlsTags) -> None:
        assert url._is_same_index(url)
        assert url._is_same_index(url.move_page(1))
        assert url._is_same_index(url.move_page(-1))

        assert not url._is_same_index(url.require("f"))
        assert not url._is_same_index(url.exclude("f"))
        assert not url._is_same_index(url.remove("a"))
        assert not url._is_same_index(url.remove("c"))
        assert not url._is_same_index(url.to_language(self.alt_language))

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_is_prev_to(self, url: UrlsTags) -> None:
        assert not url.is_prev_to(url)
        assert not url.is_prev_to(url.move_page(-1))
        assert url.is_prev_to(url.move_page(1))

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_is_next_to(self, url: UrlsTags) -> None:
        assert not url.is_next_to(url)
        assert url.is_next_to(url.move_page(-1))
        assert not url.is_next_to(url.move_page(1))

    def test_first_page(self, url: UrlsTags) -> None:
        assert url.first_page() == UrlsTags(
            language=self.base_language, page=1, required_tags=url.required_tags, excluded_tags=url.excluded_tags
        )

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_last_page(self, url: UrlsTags) -> None:
        assert url.last_page() == UrlsTags(
            language=self.base_language, page=100500, required_tags=url.required_tags, excluded_tags=url.excluded_tags
        )

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_move_page(self, url: UrlsTags) -> None:
        assert url.move_page(3) == UrlsTags(
            language=self.base_language,
            page=url.page + 3,
            required_tags=url.required_tags,
            excluded_tags=url.excluded_tags,
        )

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_move_page__too_low(self, url: UrlsTags) -> None:
        with pytest.raises(NotImplementedError):
            url.move_page(-10005000)

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_move_page__too_big(self, url: UrlsTags) -> None:
        with pytest.raises(NotImplementedError):
            url.move_page(10005000)

    def test_require(self, url: UrlsTags) -> None:
        assert url.require("f") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a", "d", "f"), excluded_tags=("c", "b", "e")
        )

    def test_require__move(self, url: UrlsTags) -> None:
        assert url.require("b") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a", "d", "b"), excluded_tags=("c", "e")
        )

    def test_require__duplicated(self, url: UrlsTags) -> None:
        assert url.require("a") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a", "d"), excluded_tags=("c", "b", "e")
        )

    def test_exclude(self, url: UrlsTags) -> None:
        assert url.exclude("f") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a", "d"), excluded_tags=("c", "b", "e", "f")
        )

    def test_exclude__move(self, url: UrlsTags) -> None:
        assert url.exclude("d") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a",), excluded_tags=("c", "b", "d", "e")
        )

    def test_exclude__duplicated(self, url: UrlsTags) -> None:
        assert url.exclude("b") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a", "d"), excluded_tags=("c", "b", "e")
        )

    def test_remove__no_tag(self, url: UrlsTags) -> None:
        assert url.remove("f") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a", "d"), excluded_tags=("c", "b", "e")
        )

    def test_remove__from_required(self, url: UrlsTags) -> None:
        assert url.remove("d") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a",), excluded_tags=("c", "b", "e")
        )

    def test_remove__from_excluded(self, url: UrlsTags) -> None:
        assert url.remove("b") == UrlsTags(
            language=self.base_language, page=1, required_tags=("a", "d"), excluded_tags=("c", "e")
        )

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_noindex(self, url: UrlsTags) -> None:  # type: ignore
        assert url.selected_tags
        assert url.is_noindex()
        assert url.move_page(1).is_noindex()
        assert url.move_page(-1).is_noindex()

    @mock.patch("brigid.domain.urls.UrlsTags.total_pages", 100500)
    def test_no_noindex_for_basic_pages_list(self) -> None:
        url = UrlsTags(language=self.base_language, page=10, required_tags=(), excluded_tags=())

        assert not url.is_noindex()
        assert not url.move_page(1).is_noindex()
        assert not url.move_page(-1).is_noindex()

    def test_total_pages_cached(self, url: UrlsTags) -> None:
        assert url._total_pages is None

        assert isinstance(url.total_pages, int)

        assert url._total_pages is not None
        assert url._total_pages == url.total_pages

    def test_get_total_pages(self) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=(), excluded_tags=())

        all_pages = storage.get_posts(language=self.base_language, require_tags=(), exclude_tags=())
        posts_per_page = storage.get_site().posts_per_page

        pages = (len(all_pages) + posts_per_page - 1) // posts_per_page

        assert pages == url.total_pages == url.move_page(1).total_pages

    def test_get_total_pages__requied_filter(self) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=("basic",), excluded_tags=())

        whole_pages = storage.get_posts(language=self.base_language, require_tags=(), exclude_tags=())

        all_pages = storage.get_posts(language=self.base_language, require_tags=("basic",), exclude_tags=())

        assert len(whole_pages) != len(all_pages)

        posts_per_page = storage.get_site().posts_per_page

        pages = (len(all_pages) + posts_per_page - 1) // posts_per_page

        assert pages == url.total_pages

    def test_get_total_pages__exclued_filter(self) -> None:
        url = UrlsTags(language=self.base_language, page=1, required_tags=(), excluded_tags=("basic",))

        whole_pages = storage.get_posts(language=self.base_language, require_tags=(), exclude_tags=())

        all_pages = storage.get_posts(language=self.base_language, require_tags=(), exclude_tags=("basic",))

        assert len(whole_pages) != len(all_pages)

        posts_per_page = storage.get_site().posts_per_page

        pages = (len(all_pages) + posts_per_page - 1) // posts_per_page

        assert pages == url.total_pages


class TestUrlsStatic:

    def test_path(self) -> None:
        assert UrlsStatic(url_path="favicon.ico").path() == "favicon.ico"

    @pytest.mark.parametrize(
        "base,url",
        [
            ("https://example.com", "https://example.com/favicon.ico"),
            ("https://example.com/blog", "https://example.com/blog/favicon.ico"),
            ("https://example.com/long/complex/prefix", "https://example.com/long/complex/prefix/favicon.ico"),
        ],
    )
    def test_favicon__prefix_variants(self, base: str, url: str) -> None:
        with mock.patch("brigid.domain.urls._base_url", return_value=base):
            assert UrlsStatic(url_path="favicon.ico").url() == url


class TestUrlsMCP:

    def test_path(self) -> None:
        assert UrlsMCP().path() == "mcp"

    @pytest.mark.parametrize(
        "prefix,path",
        [
            ("", "/mcp"),
            ("/blog", "/blog/mcp"),
            ("/long/complex/prefix", "/long/complex/prefix/mcp"),
        ],
    )
    def test_mount_path(self, prefix: str, path: str) -> None:
        site = storage.get_site()
        original_local_url = site.local_url
        original_prod_url = site.prod_url

        base_url = f"https://example.com{prefix}" if prefix else "https://example.com"

        try:
            site.local_url = base_url
            site.prod_url = base_url
            site.__dict__.pop("url", None)
            site.__dict__.pop("url_path_prefix", None)
            assert UrlsMCP().mount_path() == path
        finally:
            site.local_url = original_local_url
            site.prod_url = original_prod_url
            site.__dict__.pop("url", None)
            site.__dict__.pop("url_path_prefix", None)
