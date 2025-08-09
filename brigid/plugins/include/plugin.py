import jinja2

from brigid.plugins.plugin import Plugin
from brigid.plugins.include.settings import settings


class CorePlugin(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def templates_loader(self) -> jinja2.BaseLoader | None:
        if not settings.templates:
            return None
        return jinja2.FileSystemLoader(settings.templates, followlinks=True)


plugin = CorePlugin(slug="include")
