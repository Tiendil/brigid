import json

import fastapi
import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from brigid.library.storage import storage

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


class TestPluginStatic:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/static/plugins/theme/main.css")
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
        for language in storage.get_site().allowed_languages:
            response = client.get(f"/{language}/feeds/atom")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/atom+xml; charset=utf-8"


class TestRobots:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

    @pytest.mark.asyncio
    async def test_content(self, client: TestClient) -> None:
        expected_content = """
User-agent: *
Sitemap: http://0.0.0.0:8000/sitemap.xml
Disallow: /en/tags/
Disallow: /ru/tags/
        """

        response = client.get("/robots.txt")
        assert response.text == expected_content.strip()

    @pytest.mark.parametrize(
        "prefix",
        [
            "/blog",
            "/long/complex/prefix",
        ],
    )
    @pytest.mark.asyncio
    async def test_content__prefixed(self, client: TestClient, set_base_url, prefix: str) -> None:
        set_base_url(f"https://example.com{prefix}")

        expected_content = f"""
User-agent: *
Sitemap: https://example.com{prefix}/sitemap.xml
Disallow: {prefix}/en/tags/
Disallow: {prefix}/ru/tags/
        """

        response = client.get("/robots.txt")
        assert response.text == expected_content.strip()


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


class TestRootBehaivor:

    @pytest.mark.asyncio
    async def test_no_prefix(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 302
        assert response.headers["location"] == "http://0.0.0.0:8000/en"

    @pytest.mark.parametrize(
        "prefix",
        [
            "/blog",
            "/long/complex/prefix",
        ],
    )
    @pytest.mark.asyncio
    async def test_works__has_prefix_no_slash(self, client: TestClient, set_base_url, prefix: str) -> None:
        set_base_url(f"https://example.com{prefix}")

        response = client.get(prefix)
        assert response.status_code == 302
        assert response.headers["location"] == f"https://example.com{prefix}/en"

    @pytest.mark.parametrize(
        "prefix",
        [
            "/blog",
            "/long/complex/prefix",
        ],
    )
    @pytest.mark.asyncio
    async def test_works__has_prefix_with_slash(self, client: TestClient, set_base_url, prefix: str) -> None:
        set_base_url(f"https://example.com{prefix}")

        response = client.get(f"{prefix}/")
        assert response.status_code == 302
        assert response.headers["location"] == f"https://example.com{prefix}/en"


class TestIndexRoot:

    @pytest.mark.asyncio
    async def test_only_language(self, client: TestClient) -> None:
        for language in storage.get_site().allowed_languages:
            response = client.get(f"/{language}")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"

    @pytest.mark.asyncio
    async def test_empty_filter(self, client: TestClient) -> None:
        for language in storage.get_site().allowed_languages:
            response = client.get(f"/{language}/tags")
            assert response.status_code == 301
            assert response.headers["location"] == f"http://0.0.0.0:8000/{language}"

    @pytest.mark.asyncio
    async def test_with_filter(self, client: TestClient) -> None:
        for language in storage.get_site().allowed_languages:
            response = client.get(f"/{language}/tags/example/-wide")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestPost:

    @pytest.mark.asyncio
    async def test_works(self, client: TestClient) -> None:
        for language in storage.get_site().allowed_languages:
            response = client.get(f"/{language}/posts/post-in-two-languages")
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"


class TestSiteHtml:

    @pytest.mark.parametrize(
        "path",
        ["/en", "/en/tags/2", "/en/tags/example/-wide", "/en/posts/post-in-two-languages"],
    )
    @pytest.mark.asyncio
    async def test_html_is_rendered_in_header_and_stripped_from_metadata(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch, path: str
    ) -> None:
        site = storage.get_site()
        title = 'Blog & "news" <today>'
        subtitle = 'Ideas & "links" for readers'
        monkeypatch.setitem(
            site.languages,
            "en",
            site.languages["en"].replace(
                title='<em>Blog &amp; "news" &lt;today&gt;</em>',
                subtitle='<strong>Ideas &amp; "links"</strong> for <a href="https://example.com">readers</a>',
            ),
        )

        response = client.get(path)
        assert response.status_code == 200
        soup = BeautifulSoup(response.text, "html.parser")

        header_title = soup.select_one("header .brigid-blog-title a")
        assert header_title is not None
        assert header_title.find("em") is not None
        assert header_title.get_text() == title

        header_subtitle = soup.select_one("header > div:nth-of-type(2)")
        assert header_subtitle is not None
        assert header_subtitle.find("strong") is not None
        assert header_subtitle.find("a", href="https://example.com") is not None
        assert header_subtitle.get_text() == subtitle

        site_name = soup.select_one('meta[property="og:site_name"]')
        assert site_name is not None
        assert site_name["content"] == title

        page_title = soup.select_one("title")
        assert page_title is not None
        headline = page_title.get_text()
        for selector, attribute in (
            ('meta[property="og:title"]', "content"),
            ('link[rel="alternate"][type="application/atom+xml"]', "title"),
        ):
            element = soup.select_one(selector)
            assert element is not None
            assert element[attribute] == headline

        if "/posts/" not in path:
            assert title in headline
            for selector in ('meta[name="description"]', 'meta[property="og:description"]'):
                description = soup.select_one(selector)
                assert description is not None
                assert subtitle in description["content"]

        for script in soup.select('script[type="application/ld+json"]'):
            assert json.loads(script.get_text())["headline"] == headline
