from brigid.core import logging
from brigid.plugins.plugin import Plugin
from brigid.plugins.settings import settings

logger = logging.get_module_logger()

_plugins: list["Plugin"] | None = None
_plugins_dict: dict[str, "Plugin"] | None = None


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


def plugins_dict() -> dict[str, Plugin]:
    global _plugins_dict

    if _plugins_dict:
        return _plugins_dict

    _plugins_dict = {plugin.slug: plugin for plugin in plugins()}

    return _plugins_dict


def get_plugin(slug: str) -> Plugin | None:
    return plugins_dict().get(slug)
