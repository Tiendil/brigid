from typing import Any

import jinja2

from brigid.jinja2_render.templates import get_jinjaglobals
from brigid.plugins.core import jinjaglobals
from brigid.plugins.core.settings import settings
from brigid.plugins.plugin import Plugin


class CorePlugin(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def templates_loader(self) -> jinja2.BaseLoader:
        return jinja2.FileSystemLoader(settings.templates, followlinks=True)

    def jinjaglobals(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return get_jinjaglobals(jinjaglobals)


plugin = CorePlugin(slug="core")
