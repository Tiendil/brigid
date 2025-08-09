import jinja2

from brigid.plugins.photoswipe.settings import settings
from brigid.plugins.plugin import Plugin


class CorePlugin(Plugin):
    def __init__(self, settings, **kwargs):
        self.settings = settings
        super().__init__(**kwargs)

    def templates_loader(self) -> jinja2.BaseLoader:
        return jinja2.FileSystemLoader(settings.templates, followlinks=True)


plugin = CorePlugin(slug="photoswipe", settings=settings)
