from brigid.core import logging
from brigid.plugins.settings import settings
from brigid.plugins.plugin import Plugin


logger = logging.get_module_logger()

_plugins = None


def plugins() -> list[Plugin]:
    global _plugins

    if _plugins:
        return _plugins

    _plugins = []

    for plugin_path in settings.plugins:
        logger.info("loading_plugin", plugin=plugin_path)

        module_name, plugin_name = plugin_path.rsplit(":", 1)

        try:
            module = __import__(module_name, fromlist=[plugin_name])
        except BaseException as e:
            logger.exception("error_loading_plugin", plugin=plugin_path, exc_info=e)
            continue

        try:
            plugin = getattr(module, plugin_name)
        except BaseException as e:
            logger.exception("error_getting_plugin", plugin=plugin_path, exc_info=e)
            continue

        _plugins.append(plugin)

        logger.info("plugin_loaded", slug=plugin.slug)

    return _plugins
