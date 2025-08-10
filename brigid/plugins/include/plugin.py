import jinja2

from brigid.plugins.include.settings import settings
from brigid.plugins.plugin import Plugin


class CorePlugin(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def templates_loader(self) -> jinja2.BaseLoader | None:
        return jinja2.FileSystemLoader(settings.templates, followlinks=True)


plugin = CorePlugin(slug="include")
