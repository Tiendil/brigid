import pytest

from brigid.library.storage import storage


@pytest.fixture
def set_base_url():
    site = storage.get_site()
    original_local_url = site.local_url

    def _set(url: str) -> None:
        site.local_url = url
        site.__dict__.pop("url", None)
        site.__dict__.pop("url_path_prefix", None)

    yield _set

    site.local_url = original_local_url
    site.__dict__.pop("url", None)
    site.__dict__.pop("url_path_prefix", None)
