from typing import Any

import jinja2

from brigid.jinja2_render.settings import settings
from brigid.library.storage import storage
from brigid.plugins.utils import plugins


def get_jinjaglobals(module):

    filter_functions = {}
    global_functions = {}

    for func_name in dir(module):
        func = getattr(module, func_name)

        if getattr(func, "_is_jinjaglobal", False):
            global_functions[func_name] = func

        if getattr(func, "_is_jinjafilter", False):
            filter_functions[func_name] = func

    return global_functions, filter_functions


def fill_globals(environment):
    from brigid.jinja2_render import jinjaglobals

    environment.globals.update({"site": storage.get_site(), "storage": storage, "plugins": plugins()})

    for module in (jinjaglobals,):
        global_functions, filter_functions = get_jinjaglobals(module)

        environment.globals.update(global_functions)
        environment.filters.update(filter_functions)

    # process plugins after default globals, and in defined order to allow plugins to override them
    for plugin in plugins():
        global_functions, filter_functions = plugin.jinjaglobals()

        environment.globals.update(global_functions)
        environment.filters.update(filter_functions)


def environment():
    loader = jinja2.PrefixLoader(
        {plugin.slug: loader for plugin in plugins() if (loader := plugin.templates_loader()) is not None}
    )

    environment = jinja2.Environment(
        autoescape=True,
        trim_blocks=True,
        auto_reload=settings.templates_reload,
        undefined=jinja2.StrictUndefined,
        loader=loader,
        extensions=["jinja2.ext.loopcontrols"],
    )

    fill_globals(environment)

    return environment


_env = None


def initialize():
    global _env
    _env = environment()


def env() -> jinja2.Environment:
    if _env is None:
        initialize()

    assert _env is not None

    return _env


def render(template_name: str, context: dict[str, Any]) -> str:
    template = env().get_template(template_name)
    return template.render(context)
