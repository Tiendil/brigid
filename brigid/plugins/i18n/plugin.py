from typing import Any

from brigid.jinja2_render.templates import get_jinjaglobals
from brigid.plugins.i18n import jinjaglobals
from brigid.plugins.plugin import Plugin


class I18nPlugin(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def jinjaglobals(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return get_jinjaglobals(jinjaglobals)


plugin = I18nPlugin(slug="i18n")
