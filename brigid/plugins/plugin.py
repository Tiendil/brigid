from typing import Any

import jinja2
from markupsafe import Markup

from brigid.core import logging
from brigid.jinja2_render.entities import IndexInfo, Info, MetaInfo, PageInfo
from brigid.plugins.entities import FileInfo

logger = logging.get_module_logger()


class Plugin:

    def __init__(self, slug: str):
        self.slug = slug

    def templates_loader(self) -> jinja2.BaseLoader | None:
        return None

    def jinjaglobals(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return {}, {}

    def static_file_info(self, filename: str) -> FileInfo | None:  # pylint: disable=W0613
        return None

    def static_files(self) -> list[FileInfo]:
        return []

    def render_template_if_exists(  # noqa: CFQ002
        self,
        template_name: str,
        info: Info,
        meta: MetaInfo,
        index: IndexInfo | None = None,
        page: PageInfo | None = None,
        default: str = "",
    ) -> str:
        from brigid.jinja2_render.templates import render

        try:
            return Markup(
                render(
                    template_name,
                    {"info": info, "meta_info": meta, "index_info": index, "page_info": page, "plugin": self},
                )
            )
        except jinja2.TemplateNotFound:
            return default
        except BaseException as e:
            logger.exception("plugin_render_error", template=template_name, plugin=self.slug, exc_info=e)
            return str(e)

    def render_head(
        self, info: Info, meta: MetaInfo, index: IndexInfo | None = None, page: PageInfo | None = None
    ) -> str:
        return self.render_template_if_exists(
            f"{self.slug}/head.html.j2", info=info, meta=meta, index=index, page=page
        )

    def render_body_before_content(
        self, info: Info, meta: MetaInfo, index: IndexInfo | None = None, page: PageInfo | None = None
    ) -> str:
        return self.render_template_if_exists(
            f"{self.slug}/body_before_content.html.j2", info=info, meta=meta, index=index, page=page
        )

    def render_body_after_content(
        self, info: Info, meta: MetaInfo, index: IndexInfo | None = None, page: PageInfo | None = None
    ) -> str:
        return self.render_template_if_exists(
            f"{self.slug}/body_after_content.html.j2", info=info, meta=meta, index=index, page=page
        )

    def render_body_after_footer(
        self, info: Info, meta: MetaInfo, index: IndexInfo | None = None, page: PageInfo | None = None
    ) -> str:
        return self.render_template_if_exists(
            f"{self.slug}/body_after_footer.html.j2", info=info, meta=meta, index=index, page=page
        )
