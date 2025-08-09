
from brigid.plugins.settings import settings
from brigid.plugins.plugin import Plugin

_plugins = None


def plugins() -> list[Plugin]:
    global _plugins

    if _plugins:
        return _plugins

    _plugins = []

    for plugin_path in settings.plugins:
        module_name, plugin_name = plugin_path.rsplit(":", 1)
        module = __import__(module_name, fromlist=[plugin_name])
        plugin = getattr(module, plugin_name)

        _plugins.append(plugin)

    return _plugins
