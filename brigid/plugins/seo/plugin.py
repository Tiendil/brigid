import jinja2
from brigid.plugins.plugin import Plugin
from typing import Any

from brigid.plugins.seo.settings import settings
from brigid.theme.templates import get_jinjaglobals


class CorePlugin(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def templates_loader(self) -> jinja2.BaseLoader:
        return jinja2.FileSystemLoader(settings.templates, followlinks=True)


plugin = CorePlugin(slug="seo")
