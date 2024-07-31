
import copy
import pytest
from typing import Any

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

    def _consruct_url(self) -> UrlsBase:
        return UrlsRoot(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}"


class TestUrlsAuthor(_TestUrlsBase):

    def _consruct_url(self) -> UrlsBase:
        return UrlsAuthor(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}/about"


class TestUrlsFeedsAtom(_TestUrlsBase):

    def _consruct_url(self) -> UrlsBase:
        return UrlsFeedsAtom(language=self.base_language)

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}/feeds/atom"


class TestUrlsPost(_TestUrlsBase):

    def _consruct_url(self) -> UrlsBase:
        return UrlsPost(language=self.base_language, slug='some-slug')

    def test_url_method_redefined(self, url: UrlsBase) -> None:
        assert url.url() == f"{base_url}/{self.base_language}/posts/some-slug"

    def test_file_url(self, url: UrlsBase) -> None:
        filepath = 'images/some-image.png'
        assert url.file_url(filepath) == f"{base_url}/static/posts/some-slug/{filepath}"
