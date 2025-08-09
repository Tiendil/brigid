
from typing import Any

import jinja2

from brigid.plugins.theme.settings import settings
from brigid.plugins.plugin import Plugin
from brigid.jinja2_render.templates import get_jinjaglobals


class ThemePlugin(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def templates_loader(self) -> jinja2.BaseLoader:
        loaders = [jinja2.FileSystemLoader(settings.templates_base, followlinks=True)]

        if settings.templates_redefined:
            loaders.append(jinja2.FileSystemLoader(settings.templates_redefined, followlinks=True))

        return jinja2.ChoiceLoader(loaders)


plugin = ThemePlugin(slug="theme")
