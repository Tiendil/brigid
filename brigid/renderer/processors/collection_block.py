from typing import Any

import pydantic
from pymdownx.blocks import BlocksExtension

from brigid.core.entities import BaseEntity
from brigid.renderer.processors.toml_block import TomlBlock


class CollectionModel(BaseEntity):
    id: str
    css_class: str | None = None

    model_config = pydantic.ConfigDict(frozen=False)


class CollectionBlock(TomlBlock):
    NAME = "brigid-collection"
    models = CollectionModel
    root_tag = "div"
    template: str = "./blocks/collection.html.j2"

    def root_css_classes(self, data: Any) -> list[str]:
        classes = ["brigid-collection", data.css_class]
        return [x for x in classes if x]


class CollectionBlockExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(CollectionBlock, self.getConfigs())
