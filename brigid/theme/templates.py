from typing import Any

import jinja2

from brigid.theme.settings import settings


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
    from brigid.theme import jinjaglobals

    for module in (jinjaglobals,):
        global_functions, filter_functions = get_jinjaglobals(module)

        environment.globals.update(global_functions)
        environment.filters.update(filter_functions)


def environment():
    loader = jinja2.FileSystemLoader(settings.templates.directory, followlinks=True)

    environment = jinja2.Environment(
        autoescape=True,
        trim_blocks=True,
        auto_reload=settings.templates.reload,
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
