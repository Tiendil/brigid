import copy
import pytest
from typing import Any
from unittest import mock

from brigid.domain.urls import normalize_url, UrlsBase, UrlsFeedsAtom, UrlsAuthor, UrlsPost, UrlsTags, UrlsSiteMapFull, UrlsRoot


base_url = 'http://0.0.0.0:8000'


class TestNormalizeUrl:

    @pytest.mark.parametrize('url_in',
                             ['',
                              'example.com',
                              'example.com/////',
                              'child.example.com//'])
    def test_wrong_url(self, url_in):
        with pytest.raises(NotImplementedError):
            normalize_url(url_in)


    @pytest.mark.parametrize('url_in,url_out',
                             [('https://example.com', 'https://example.com'),
                              ('https://example.com/', 'https://example.com'),
                              ('https://example.com//', 'https://example.com'),
                              ('https://example.com/////', 'https://example.com'),
                              ('https://child.example.com//', 'https://child.example.com'),
                              ('https://example.com/path/b/c', 'https://example.com/path/b/c'),
                              ('https://example.com/path/b/c/', 'https://example.com/path/b/c'),
                              ('https://example.com//path///b///c', 'https://example.com/path/b/c'),
                              ('https://example.com/path/b/c?', 'https://example.com/path/b/c'),
                              ('http://example.com//path///b///c',
                               'http://example.com/path/b/c')])
    def test_normalization(self, url_in: str, url_out: str):
        assert normalize_url(url_in) == url_out


class _TestUrlsBase:

    base_language = 'en'
    alt_language = 'ru'

    @pytest.fixture
    def url(self):
        return self._consruct_url()

    def _consruct_url(self) -> Any:
        raise NotImplementedError()

    def test_base_initialized(self, url: UrlsBase) -> None:
        assert url.language == self.base_language

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert isinstance(url.url(), str)

    def test_file_url(self, url: UrlsBase) -> None:
        with pytest.raises(NotImplementedError):
            url.file_url('')

    def test_to_root(self, url: UrlsBase) -> None:
        assert url.to_root() == UrlsRoot(language=self.base_language)

    def test_to_feeds_atom(self, url: UrlsBase) -> None:
        assert url.to_feeds_atom() == UrlsFeedsAtom(language=self.base_language)

    def test_to_author(self, url: UrlsBase) -> None:
        assert url.to_author() == UrlsAuthor(language=self.base_language)

    def test_to_post(self, url: UrlsBase) -> None:
        assert url.to_post('xxx') == UrlsPost(language=self.base_language, slug='xxx')

    def test_to_filter(self, url: UrlsBase) -> None:
        filter_url = url.to_filter(page=13,
                                   require=('a', 'b'),
                                   exclude=('c', 'd', 'e'))

        expected_filter_url = UrlsTags(
            language=self.base_language,
            page=13,
            required_tags=('a', 'b'),
            excluded_tags=('c', 'd', 'e'),
        )

        assert filter_url == expected_filter_url

    def test_language(self, url: UrlsBase) -> None:
        expected_url = copy.deepcopy(url)
        expected_url.language = self.alt_language

        assert url.to_language(self.alt_language) == expected_url

    def test_site_map_full(self, url: UrlsBase) -> None:
        assert url.to_site_map_full() == UrlsSiteMapFull(language=self.base_language)


class TestUrlsBase(_TestUrlsBase):

    def _consruct_url(self) -> UrlsBase:
        return UrlsBase(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        with pytest.raises(NotImplementedError):
            url.url()


class TestUrlsRoot(_TestUrlsBase):

    def _consruct_url(self) -> UrlsRoot:
        return UrlsRoot(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}"


class TestUrlsAuthor(_TestUrlsBase):

    def _consruct_url(self) -> UrlsAuthor:
        return UrlsAuthor(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}/about"


class TestUrlsFeedsAtom(_TestUrlsBase):

    def _consruct_url(self) -> UrlsFeedsAtom:
        return UrlsFeedsAtom(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}/feeds/atom"


class TestUrlsPost(_TestUrlsBase):

    def _consruct_url(self) -> UrlsPost:
        return UrlsPost(language=self.base_language, slug='some-slug')

    def test_initialized(self, url: UrlsBase) -> None:
        assert url.slug == 'some-slug'

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}/posts/some-slug"

    def test_file_url(self, url: UrlsBase) -> None:
        filepath = 'images/some-image.png'
        assert url.file_url(filepath) == f"{base_url}/static/posts/some-slug/{filepath}"


class TestUrlsTags(_TestUrlsBase):

    def _consruct_url(self) -> UrlsTags:
        return UrlsTags(language=self.base_language,
                        page=13,
                        required_tags=('a', 'd'),
                        excluded_tags=('c', 'b', 'e'))

    def test_initialized(self, url: UrlsBase) -> None:
        assert url.page == 13
        assert url.required_tags == {'a', 'd'}
        assert url.excluded_tags == {'c', 'b', 'e'}
        assert url.selected_tags == {'a', 'b', 'c', 'd', 'e'}

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}/tags/a/-b/-c/d/-e/13"

    def test_url_method__empty(self) -> None:
        url = UrlsTags(language=self.base_language,
                        page=1,
                        required_tags=(),
                        excluded_tags=())

        assert url.url() == f"{base_url}/{self.base_language}"

    def test_url_method__only_required(self) -> None:
        url = UrlsTags(language=self.base_language,
                        page=1,
                        required_tags=('a', 'b'),
                        excluded_tags=())

        assert url.url() == f"{base_url}/{self.base_language}/tags/a/b"

    def test_url_method__only_excluded(self) -> None:
        url = UrlsTags(language=self.base_language,
                        page=1,
                        required_tags=(),
                        excluded_tags=('a', 'b'))

        assert url.url() == f"{base_url}/{self.base_language}/tags/-a/-b"

    def test_url_method__only_page(self) -> None:
        url = UrlsTags(language=self.base_language,
                        page=13,
                        required_tags=(),
                        excluded_tags=())

        assert url.url() == f"{base_url}/{self.base_language}/tags/13"

    @mock.patch('brigid.domain.urls.UrlsTags.total_pages', 100500)
    def test_is_same_index(self, url: UrlsBase) -> None:
        assert url.is_same_index(url)
        assert url.is_same_index(url.move_page(1))
        assert url.is_same_index(url.move_page(-1))

        assert not url.is_same_index(url.require('f'))
        assert not url.is_same_index(url.exclude('f'))
        assert not url.is_same_index(url.remove('a'))
        assert not url.is_same_index(url.remove('c'))
        assert not url.is_same_index(url.to_language(self.alt_language))

    @mock.patch('brigid.domain.urls.UrlsTags.total_pages', 100500)
    def test_is_prev_to(self, url: UrlsBase) -> None:
        assert not url.is_prev_to(url)
        assert not url.is_prev_to(url.move_page(-1))
        assert url.is_prev_to(url.move_page(1))

    @mock.patch('brigid.domain.urls.UrlsTags.total_pages', 100500)
    def test_is_next_to(self, url: UrlsBase) -> None:
        assert not url.is_next_to(url)
        assert url.is_next_to(url.move_page(-1))
        assert not url.is_next_to(url.move_page(1))
