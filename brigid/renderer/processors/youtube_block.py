from typing import Any

import pydantic
from pymdownx.blocks import BlocksExtension

from brigid.core.entities import BaseEntity
from brigid.renderer.processors.toml_block import TomlBlock


class YouTubeModel(BaseEntity):
    caption: str
    id: str
    css_class: str | None = None

    model_config = pydantic.ConfigDict(frozen=False)

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/embed/{self.id}"


class YouTubeBlock(TomlBlock):
    NAME = "brigid-youtube"
    models = YouTubeModel
    root_tag = "figure"
    template = "./blocks/youtube.html.j2"

    def root_css_classes(self, data: Any) -> list[str]:
        classes = ["brigid-youtube", data.css_class]
        return [x for x in classes if x]


class YouTubeBlockExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(YouTubeBlock, self.getConfigs())
