from typing import Any

import pydantic
from pymdownx.blocks import BlocksExtension

from brigid.core.entities import BaseEntity
from brigid.renderer.context import render_context
from brigid.renderer.processors.toml_block import TomlBlock


class CollectionModel(BaseEntity):
    id: str
    css_class: str | None = None

    model_config = pydantic.ConfigDict(frozen=False)


class CollectionBlock(TomlBlock):
    NAME = "brigid-collection"
    models = CollectionModel
    root_tag = "div"

    def root_css_classes(self, data: Any) -> list[str]:
        classes = ["brigid-collection", data.css_class]
        return [x for x in classes if x]

    def process_data(self, data: Any) -> str:
        from brigid.theme.templates import render

        context = render_context.get()

        return render(
            "./blocks/collection.html.j2",
            {
                "collection_data": data,
                # TODO: rename all arguments in all blogs to "current_"
                # TODO: add current_page everywhere
                "current_article": context.article,
                "current_page": context.page,
            },
        )


class CollectionBlockExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(CollectionBlock, self.getConfigs())
