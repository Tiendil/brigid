import pytest

from brigid.domain import request_context


@pytest.fixture
def set_base_url():
    site = request_context.get("storage").get_site()
    original_local_url = site.local_url

    def _set(url: str) -> None:
        site.local_url = url
        site.__dict__.pop("url", None)
        site.__dict__.pop("url_path_prefix", None)

    yield _set

    site.local_url = original_local_url
    site.__dict__.pop("url", None)
    site.__dict__.pop("url_path_prefix", None)
