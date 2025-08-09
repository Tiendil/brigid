import jinja2
from typing import Any


class Plugin:

    def __init__(self, slug: str):
        self.slug = slug

    def templates_loader(self) -> jinja2.BaseLoader | None:
        return None

    def jinjaglobals(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return {}, {}

    def render_head(self) -> str:
        return ""

    def render_body_before_content(self) -> str:
        return ""

    def render_body_after_content(self) -> str:
        return ""
