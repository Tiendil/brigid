import fastapi
import pytest
from fastapi.testclient import TestClient

from brigid.domain import request_context

############################################################################
# ATTENTION: this tests do not cover some cases of request_context usage
#            because it setupped automatically in conftest.py for all tests.
#            In the future we can move this fixture from the global scope to the test level.
############################################################################


class TestFavicon:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/favicon.ico")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/x-icon"


class TestSiteMap:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml; charset=utf-8"


class TestMainCss:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/static/main.css")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/css; charset=utf-8"


class TestStaticFile:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/static/posts/galery-types/images/image-1.jpg")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"


class TestFeedAtom:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        for language in request_context.get("storage").get_site().allowed_languages:
            response = client.get(f"/{language}/feeds/atom")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/atom+xml; charset=utf-8"


class TestRobots:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


class TestError:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        with pytest.raises(ZeroDivisionError):
            client.get("/test-error")

    @pytest.mark.asyncio
    async def test_exception_processing_works(self, app: fastapi.FastAPI) -> None:
        client = TestClient(app, raise_server_exceptions=False, follow_redirects=False)
        response = client.get("/test-error")
        assert response.status_code == 500


class TestRoot:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 302
        assert response.headers["location"] == "http://0.0.0.0:8000/en"


class TestIndexRoot:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        for language in request_context.get("storage").get_site().allowed_languages:
            response = client.get(f"/{language}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestIndexRootWithEmptyFilter:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        for language in request_context.get("storage").get_site().allowed_languages:
            response = client.get(f"/{language}/tags")
            assert response.status_code == 301
            assert response.headers["location"] == f"http://0.0.0.0:8000/{language}"


class TestIndexWithFilter:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        for language in request_context.get("storage").get_site().allowed_languages:
            response = client.get(f"/{language}/tags/example/-wide")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestPost:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        for language in request_context.get("storage").get_site().allowed_languages:
            response = client.get(f"/{language}/posts/post-in-two-languages")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"
