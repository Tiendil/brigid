import copy

import pytest

from brigid.application.settings import settings
from brigid.domain.entities import Environment
from brigid.library.storage import storage


class TestSite:

    @pytest.fixture
    def site(self):
        source_site = copy.deepcopy(storage.get_site())
        return source_site.__class__(**source_site.model_dump())

    @pytest.fixture
    def set_environment(self):
        original_environment = settings.environment

        def _set(environment: Environment) -> None:
            settings.environment = environment

        yield _set

        settings.environment = original_environment

    @pytest.mark.parametrize(
        "environment,expected_url",
        [
            (Environment.prod, "https://example.com"),
            (Environment.local, "http://0.0.0.0:8000"),
        ],
    )
    def test_url_choice(self, site, set_environment, environment: Environment, expected_url: str) -> None:

        # check default values
        assert str(site.prod_url) == "https://example.com/"
        assert str(site.local_url) == "http://0.0.0.0:8000/"

        set_environment(environment)
        assert site.url == expected_url

    @pytest.mark.parametrize(
        "configured_url,expected_url,expected_prefix",
        [
            ("https://example.com", "https://example.com", ""),
            ("https://example.com/blog", "https://example.com/blog", "/blog"),
            (
                "https://example.com/long/complex/prefix",
                "https://example.com/long/complex/prefix",
                "/long/complex/prefix",
            ),
        ],
    )
    def test_url_and_url_path_prefix__prod(
        self,
        site,
        set_environment,
        configured_url: str,
        expected_url: str,
        expected_prefix: str,
    ) -> None:
        site.prod_url = configured_url
        set_environment(Environment.prod)

        assert site.url == expected_url
        assert site.url_path_prefix == expected_prefix

    @pytest.mark.parametrize(
        "configured_url,expected_url,expected_prefix",
        [
            ("https://example.com", "https://example.com", ""),
            ("https://example.com/blog", "https://example.com/blog", "/blog"),
            (
                "https://example.com/long/complex/prefix",
                "https://example.com/long/complex/prefix",
                "/long/complex/prefix",
            ),
        ],
    )
    def test_url_and_url_path_prefix__local(
        self,
        site,
        set_environment,
        configured_url: str,
        expected_url: str,
        expected_prefix: str,
    ) -> None:
        site.local_url = configured_url
        set_environment(Environment.local)

        assert site.url == expected_url
        assert site.url_path_prefix == expected_prefix
