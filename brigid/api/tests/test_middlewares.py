import fastapi
import pytest
from fastapi.testclient import TestClient

from brigid.api import middlewares
from brigid.library.entities import Redirects
from brigid.library.storage import storage


class TestRedirects:

    @pytest.fixture
    def set_redirects(self):
        original_redirects = storage.get_redirects()

        def _set(redirects: Redirects) -> None:
            storage.set_redirects(redirects)

        yield _set

        storage.set_redirects(original_redirects)

    @pytest.mark.asyncio
    async def test_external_target_passthrough(self, client: TestClient, set_base_url, set_redirects) -> None:
        set_base_url("https://example.com/blog")
        set_redirects(Redirects(permanent={"/old": "https://external.example/path"}))

        response = client.get("/blog/old")
        assert response.status_code == 301
        assert response.headers["location"] == "https://external.example/path"

    @pytest.mark.asyncio
    async def test_root_relative_target_rebased_with_prefix(
        self, client: TestClient, set_base_url, set_redirects
    ) -> None:
        set_base_url("https://example.com/blog")
        set_redirects(Redirects(permanent={"/old": "/tags/"}))

        response = client.get("/blog/old")
        assert response.status_code == 301
        assert response.headers["location"] == "/blog/tags/"

    @pytest.mark.asyncio
    async def test_invalid_relative_target_fails(self, app: fastapi.FastAPI, set_base_url, set_redirects) -> None:
        set_base_url("https://example.com/blog")
        set_redirects(Redirects(permanent={"/old": "tags/"}))

        client = TestClient(app, raise_server_exceptions=False, follow_redirects=False)
        response = client.get("/blog/old")

        assert response.status_code == 500


class TestContentLanguageMiddleware:

    @pytest.mark.asyncio
    async def test_prefixed_path_sets_header(self, set_base_url) -> None:
        set_base_url("https://example.com/blog")

        async def call_next(_: fastapi.Request) -> fastapi.Response:
            return fastapi.Response(status_code=200)

        request = fastapi.Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/blog/en",
                "headers": [],
                "query_string": b"",
                "client": ("test", 123),
                "server": ("test", 80),
                "scheme": "http",
                "root_path": "",
            }
        )

        response = await middlewares.set_content_language(request, call_next)
        assert response.headers["content-language"] == "en"


class TestRemoveDoubleSlashesMiddleware:

    @pytest.mark.asyncio
    async def test_redirects_non_prefixed_path(self, client: TestClient) -> None:
        response = client.get("/en//posts/post-in-two-languages")
        assert response.status_code == 301
        assert response.headers["location"] == "/en/posts/post-in-two-languages"

    @pytest.mark.asyncio
    async def test_redirects_prefixed_path(self, client: TestClient, set_base_url) -> None:
        set_base_url("https://example.com/blog")

        response = client.get("/blog/en//posts/post-in-two-languages")
        assert response.status_code == 301
        assert response.headers["location"] == "/blog/en/posts/post-in-two-languages"


class TestRemoveTrailingSlashMiddleware:

    @pytest.mark.asyncio
    async def test_redirects_non_prefixed_path(self, client: TestClient) -> None:
        response = client.get("/en/")
        assert response.status_code == 301
        assert response.headers["location"] == "/en"

    @pytest.mark.asyncio
    async def test_redirects_prefixed_path(self, client: TestClient, set_base_url) -> None:
        set_base_url("https://example.com/blog")

        response = client.get("/blog/en/")
        assert response.status_code == 301
        assert response.headers["location"] == "/blog/en"
