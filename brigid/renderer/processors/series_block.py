from typing import Any

import pydantic
from pymdownx.blocks import BlocksExtension

from brigid.core.entities import BaseEntity
from brigid.renderer.processors.toml_block import TomlBlock


class SeriesModel(BaseEntity):
    tag: str
    css_class: str | None = None

    model_config = pydantic.ConfigDict(frozen=False)


class SeriesBlock(TomlBlock):
    NAME = "brigid-series"
    models = SeriesModel
    root_tag = "div"
    template: str = "./blocks/series.html.j2"

    def root_css_classes(self, data: Any) -> list[str]:
        classes = ["brigid-series", data.css_class]
        return [x for x in classes if x]


class SeriesBlockExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(SeriesBlock, self.getConfigs())
