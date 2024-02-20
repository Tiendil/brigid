import pathlib

from markupsafe import Markup

from brigid.domain.urls import UrlsRoot
from brigid.library.entities import Page
from brigid.library.storage import Storage, storage
from brigid.renderer.markdown_render import render_page as markdown_render_page
from brigid.renderer.markdown_render import render_page_intro as markdown_render_page_intro
from brigid.renderer.markdown_render import render_text as markdown_render_text
from brigid.renderer.static_files import ImageInfo, files
from brigid.theme.default_translations import translations
from brigid.theme.settings import PhotoSwipe, settings
from brigid.theme.utils import jinjafilter, jinjaglobal


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


@jinjaglobal
def translate_theme(language: str, text_id: str) -> str:
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
