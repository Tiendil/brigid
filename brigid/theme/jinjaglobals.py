import os
import pathlib
from typing import Any

from markupsafe import Markup

from brigid.domain import constants as domain_constants
from brigid.domain import request_context as d_request_context
from brigid.domain.urls import UrlsRoot
from brigid.library import utils as l_utils
from brigid.library.entities import Page, PageSeriesInfo
from brigid.library.series import get_page_series_info
from brigid.library.storage import Storage, storage
from brigid.renderer.markdown_render import render_page as markdown_render_page
from brigid.renderer.markdown_render import render_page_intro as markdown_render_page_intro
from brigid.renderer.markdown_render import render_text as markdown_render_text
from brigid.renderer.static_files import ImageInfo, files
from brigid.theme.default_translations import translations
from brigid.theme.settings import PhotoSwipe, settings
from brigid.theme.utils import jinjafilter, jinjaglobal


@jinjafilter
def upper_first(text: str) -> str:
    return text[0].upper() + text[1:]


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
def get_storage() -> Storage:
    return storage


@jinjaglobal
def photoswipe_settings() -> PhotoSwipe:
    return settings.photoswipe


@jinjaglobal
def image_info(path: pathlib.Path) -> ImageInfo:
    return files.image_info(path)


@jinjaglobal
def root_url(language: str) -> UrlsRoot:
    return UrlsRoot(language=language)


@jinjaglobal
def translate_tag(language: str, tag: str) -> str:
    site = storage.get_site()
    return site.languages[language].tags_translations[tag]


def _translate(language: str, text_id: str) -> str:
    site = storage.get_site()

    if text_id in site.languages[language].theme_translations:
        return site.languages[language].theme_translations[text_id]

    if language not in translations:
        language = site.default_language

    if language not in translations:
        language = "en"

    if text_id in translations[language]:
        return translations[language][text_id]

    return text_id


@jinjaglobal
def translate_theme(language: str, text_id: str) -> str:
    return Markup(_translate(language, text_id))


@jinjaglobal
def test_marker(marker: str) -> str:

    if not os.environ.get("BRIGID_TESTS_RUNNING"):
        return ""

    return Markup(marker)


@jinjaglobal
def brigid_repository() -> str:
    return domain_constants.brigid_repository


@jinjaglobal
def request_context_get(name: str) -> Any:
    return d_request_context.get(name)


@jinjafilter
def to_str(value: Any) -> str:
    return str(value)


@jinjaglobal
def page_series_info(page: Page) -> PageSeriesInfo:
    return get_page_series_info(page)


@jinjaglobal
def page_title(page: Page, short: bool = False) -> str:
    return l_utils.page_title(page=page, short=short)
