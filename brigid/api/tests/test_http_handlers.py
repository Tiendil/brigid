from fastapi.testclient import TestClient
import pytest


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
        assert response.headers["content-type"] == "application/xml"
