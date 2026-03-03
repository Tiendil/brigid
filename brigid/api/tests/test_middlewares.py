import fastapi
import pytest
from fastapi.testclient import TestClient

from brigid.api import middlewares
from brigid.library.entities import Redirects
from brigid.library.storage import storage


def make_request(path: str) -> fastapi.Request:
    return fastapi.Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": b"",
            "client": ("test", 123),
            "server": ("test", 80),
            "scheme": "http",
            "root_path": "",
        }
    )


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

        request = make_request("/blog/en")

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

    @pytest.mark.asyncio
    async def test_does_not_redirect_prefixed_root(self, set_base_url) -> None:
        set_base_url("https://example.com/blog")

        async def call_next(_: fastapi.Request) -> fastapi.Response:
            return fastapi.Response(status_code=204)

        response = await middlewares.remove_trailing_slash(make_request("/blog/"), call_next)
        assert response.status_code == 204


class TestPrefixedRootToSlashMiddleware:

    @pytest.mark.asyncio
    async def test_redirects_prefixed_root_to_slash(self, set_base_url) -> None:
        set_base_url("https://example.com/blog")

        async def call_next(_: fastapi.Request) -> fastapi.Response:
            raise NotImplementedError("call_next should not be called for prefix root redirect")

        response = await middlewares.prefixed_root_to_slash(make_request("/blog"), call_next)
        assert response.status_code == 301
        assert response.headers["location"] == "/blog/"

    @pytest.mark.asyncio
    async def test_passes_prefixed_root_with_slash(self, set_base_url) -> None:
        set_base_url("https://example.com/blog")

        async def call_next(_: fastapi.Request) -> fastapi.Response:
            return fastapi.Response(status_code=204)

        response = await middlewares.prefixed_root_to_slash(make_request("/blog/"), call_next)
        assert response.status_code == 204
