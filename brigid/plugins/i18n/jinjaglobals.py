from markupsafe import Markup

from brigid.jinja2_render.utils import jinjaglobal
from brigid.library.storage import storage
from brigid.plugins.i18n.default_translations import translations


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
