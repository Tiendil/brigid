from unittest import mock

from brigid.domain.entities import Environment
from brigid.library.storage import storage


class TestSite:

    def test_url_choice(self) -> None:
        site = storage.get_site()

        # check default values
        assert str(site.prod_url) == "https://example.com/"
        assert str(site.local_url) == "http://0.0.0.0:8000/"

        del site.url

        with mock.patch("brigid.application.settings.settings.environment", Environment.prod):
            assert site.url == "https://example.com"

        del site.url

        with mock.patch("brigid.application.settings.settings.environment", Environment.local):
            assert site.url == "http://0.0.0.0:8000"
