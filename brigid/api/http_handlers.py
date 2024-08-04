import pathlib

import fastapi
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse

from brigid.api import renderers
from brigid.api.sitemaps import build_sitemap_xml
from brigid.api.static_cache import cache
from brigid.api.utils import choose_language
from brigid.core import logging
from brigid.domain.urls import UrlsRoot
from brigid.library.storage import storage

router = fastapi.APIRouter()

logger = logging.get_module_logger()


####################
# Static files
####################


@router.get("/favicon.ico", response_model=None)
async def favicon() -> FileResponse | HTMLResponse:

    site = storage.get_site()

    if site.favicon is None:
        return HTMLResponse(content="")

    path = site.path.parent / site.favicon
    cache().set("/favicon.ico", path)

    return FileResponse(path, media_type="image/x-icon")


@router.get("/sitemap.xml")
async def site_map() -> PlainTextResponse:
    content = build_sitemap_xml()
    return PlainTextResponse(content, media_type="application/xml; charset=utf-8")


@router.get("/static/main.css")
async def page_css() -> FileResponse:
    css_file = pathlib.Path(__file__).parent.parent / "theme" / "static" / "main.css"

    cache().set("/static/main.css", css_file)

    return FileResponse(css_file, media_type="text/css")


@router.get("/static/posts/{article_slug}/{filename:path}")
async def static_file(request: fastapi.Request, article_slug: str, filename: str) -> FileResponse:
    article = storage.get_article(slug=article_slug)

    # TODO: could it be a security breach?
    path = article.path.parent / filename

    cache().set(request.url.path, path)

    # TODO: set media types according to file extension
    return FileResponse(path)


####################
# Technical routers
####################


@router.get("/{language}/feeds/atom")
async def feed_atom(language: str) -> HTMLResponse:
    return renderers.render_atom_feed(language)


# TODO: add RSS feed


@router.get("/robots.txt")
async def robots() -> PlainTextResponse:
    # language is not important here
    root_url = UrlsRoot(language="en")

    content = f"""\
User-agent: *
Sitemap: {root_url.to_site_map_full().url()}
"""

    return PlainTextResponse(content)


####################
# Content routers
####################


@router.get("/test-error")
async def test_error() -> HTMLResponse:
    1 / 0
    return HTMLResponse(content="This should not be shown")


@router.get("/")
async def root(request: fastapi.Request) -> RedirectResponse:
    language = choose_language(request)
    # TODO: show info to the user that language was chosen automatically
    return RedirectResponse(UrlsRoot(language=language).url(), status_code=302)


@router.get("/{language}")
async def blog_index(language: str) -> HTMLResponse:
    return renderers.render_index(language=language, raw_tags="")


@router.get("/{language}/tags")
async def tags_index_zero(language: str) -> RedirectResponse:
    return RedirectResponse(UrlsRoot(language=language).url(), status_code=301)


@router.get("/{language}/tags/{tags:path}")
async def tags_index(language: str, tags: str = "") -> HTMLResponse:
    return renderers.render_index(language=language, raw_tags=tags)


@router.get("/{language}/posts/{article_slug}")
async def page_article(language: str, article_slug: str) -> HTMLResponse:
    return renderers.render_page(language, article_slug)
