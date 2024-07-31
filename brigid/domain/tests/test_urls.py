
import pytest

from brigid.domain.urls import normalize_url


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
