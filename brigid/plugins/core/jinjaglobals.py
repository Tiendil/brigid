from typing import Any

from brigid.jinja2_render.utils import jinjafilter


@jinjafilter
def upper_first(text: str) -> str:
    return text[0].upper() + text[1:]


@jinjafilter
def to_str(value: Any) -> str:
    return str(value)
