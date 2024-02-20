import traceback
import xml.etree.ElementTree as etree  # noqa: S405
from typing import Any

import pydantic
import toml
from pymdownx.blocks.block import Block

from brigid.renderer.context import render_context

_renderer = None


class TomlBlock(Block):
    NAME: str = NotImplemented
    models: type[pydantic.BaseModel] = NotImplemented
    root_tag: str = "div"

    def root_css_classes(self, data: Any) -> list[str]:
        return []

    def on_create(self, parent):
        return etree.SubElement(parent, self.root_tag)

    def on_markdown(self) -> str:
        return "raw"

    def on_end(self, block: etree.Element) -> None:
        try:
            if block.text is None:
                raise NotImplementedError("Block text is None")

            data = toml.loads(block.text)

            model = None

            model = pydantic.TypeAdapter(self.models).validate_python(data)
            new_text = self.process_data(model)

            block.text = self.md.htmlStash.store(new_text)

            if model:
                block.set("class", " ".join(self.root_css_classes(model)))

        except Exception as e:
            new_text = f"Error: {traceback.format_exc()}".replace("\n", "<br>")

            context = render_context.get()

            context.add_error(failed_text="unknown", message=f"Error while rendering block: {e}")

    def process_data(self, data: Any) -> str:
        raise NotImplementedError()
