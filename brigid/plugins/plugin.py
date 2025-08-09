import jinja2
from typing import Any
from brigid.theme.entities import MetaInfo, Info, Template, IndexInfo, PageInfo
from markupsafe import Markup


class Plugin:

    def __init__(self, slug: str):
        self.slug = slug

    def templates_loader(self) -> jinja2.BaseLoader | None:
        return None

    def jinjaglobals(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return {}, {}

    def render_template_if_exists(self,
                                  template_name: str,
                                  info: Info,
                                  meta: MetaInfo,
                                  index: IndexInfo | None = None,
                                  page: PageInfo | None = None,
                                  default: str = "") -> str:
        from brigid.theme.templates import render
        try:
            return Markup(render(template_name,
                          {
                              "info": info,
                              "meta": meta,
                              "index": index,
                              "page": page,
                              'plugin': self
                          },
                          ))
        except jinja2.TemplateNotFound:
            return default

    def render_head(self,
                    info: Info,
                    meta: MetaInfo,
                    index: IndexInfo | None = None,
                    page: PageInfo | None = None) -> str:
        return self.render_template_if_exists(
            f"{self.slug}/head.html",
            info=info,
            meta=meta,
            index=index,
            page=page)

    def render_body_before_content(self,
                                   info: Info,
                                   meta: MetaInfo,
                                   index: IndexInfo | None = None,
                                   page: PageInfo | None = None) -> str:
        return self.render_template_if_exists(
                f"{self.slug}/body_before_content.html",
                info=info,
                meta=meta,
                index=index,
                page=page)

    def render_body_after_content(self,
                                  info: Info,
                                  meta: MetaInfo,
                                  index: IndexInfo | None = None,
                                  page: PageInfo | None = None) -> str:
        return self.render_template_if_exists(
                f"{self.slug}/body_after_content.html",
                info=info,
                meta=meta,
                index=index,
                page=page)
