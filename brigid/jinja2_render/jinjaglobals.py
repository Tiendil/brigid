import os
import pathlib
from typing import Any

from markupsafe import Markup

from brigid.domain import request_context as d_request_context
from brigid.domain.urls import UrlsPlugin, UrlsRoot
from brigid.jinja2_render.utils import jinjafilter, jinjaglobal
from brigid.library import utils as l_utils
from brigid.library.entities import Page, PageSeriesInfo
from brigid.library.series import get_page_series_info
from brigid.markdown_render.markdown_render import render_page as markdown_render_page
from brigid.markdown_render.markdown_render import render_page_intro as markdown_render_page_intro
from brigid.markdown_render.markdown_render import render_text as markdown_render_text
from brigid.markdown_render.static_files import ImageInfo, files


@jinjafilter
def render_page(page: Page) -> str:
    return Markup(markdown_render_page(page=page).content)


@jinjafilter
def render_page_intro(page: Page) -> str:
    return Markup(markdown_render_page_intro(page=page).content)


@jinjafilter
def render_text(text: str) -> str:
    return Markup(markdown_render_text(text).content)


@jinjaglobal
def image_info(path: pathlib.Path) -> ImageInfo:
    return files.image_info(path)


@jinjaglobal
def root_url(language: str) -> UrlsRoot:
    return UrlsRoot(language=language)


@jinjaglobal
def plugin_url(plugin: str, language: str) -> UrlsPlugin:
    return UrlsPlugin(plugin, language=language)


@jinjaglobal
def test_marker(marker: str) -> str:

    if not os.environ.get("BRIGID_TESTS_RUNNING"):
        return ""

    return Markup(marker)


@jinjaglobal
def request_context_get(name: str) -> Any:
    return d_request_context.get(name)


@jinjaglobal
def page_series_info(page: Page) -> PageSeriesInfo:
    return get_page_series_info(page)


@jinjaglobal
def page_title(page: Page, short: bool = False) -> str:
    return l_utils.page_title(page=page, short=short)
