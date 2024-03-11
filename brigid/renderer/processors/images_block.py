from typing import Any

import pydantic
from pymdownx.blocks import BlocksExtension

from brigid.core.entities import BaseEntity
from brigid.domain.html import strip_html
from brigid.renderer.processors.toml_block import TomlBlock

# TODO: remove duplicated code


class ImageMixing:

    @pydantic.field_validator("alt")
    @classmethod
    def escape_alt(cls, v: str | None, info: pydantic.ValidationInfo) -> str | None:
        if v is None:
            return v

        return strip_html(v)


class Image(ImageMixing, BaseEntity):
    src: str
    alt: str | None = None

    # TODO: add caption to the image to show in the lightbox

    model_config = pydantic.ConfigDict(frozen=False)


class ImagesModel(BaseEntity):
    caption: str | None = None
    images: list[Image]

    # TODO: rename to css_class
    galery_class: str | None = None

    model_config = pydantic.ConfigDict(frozen=False)

    @pydantic.field_validator("images")
    @classmethod
    def minimum_1_image(cls, v: list[Image], info: pydantic.ValidationInfo) -> list[Image]:
        if len(v) < 1:
            raise ValueError("at least one image is required")

        return v

    @pydantic.model_validator(mode="after")
    def first_image_alt_from_caption(self) -> "ImagesModel":

        if self.caption is not None and self.images[0].alt is None:
            self.images[0].alt = self.caption

        return self

    @pydantic.model_validator(mode="after")
    def all_images_must_have_alts(self) -> "ImagesModel":
        for image in self.images:
            if image.alt is None:
                raise ValueError("alt must be present")

        return self

    @pydantic.model_validator(mode="after")
    def default_galery_class(self) -> "ImagesModel":
        if self.galery_class is None:
            self.galery_class = f"brigid-images-{len(self.images)}"

        return self


class ImageModel(ImageMixing, BaseEntity):
    src: str
    alt: str | None = None
    caption: str | None = None
    galery_class: str = "brigid-images-1"

    model_config = pydantic.ConfigDict(frozen=False)

    @pydantic.model_validator(mode="after")
    def alt_or_caption(self) -> "ImageModel":
        if self.alt is None and self.caption is None:
            raise ValueError("alt or caption must be present")

        if self.alt is None and self.caption is not None:
            self.alt = self.caption

        return self


class ImagesBlock(TomlBlock):
    NAME = "brigid-images"
    models = ImageModel | ImagesModel
    root_tag = "figure"
    template = "./blocks/images.html.j2"

    def root_css_classes(self, data: ImagesModel) -> list[str]:
        assert data.galery_class
        return ["brigid-images", data.galery_class]

    def process_data(self, data: Any) -> ImagesModel:
        if isinstance(data, ImageModel):
            return ImagesModel(
                caption=data.caption,
                images=[Image(src=data.src, alt=data.alt)],
                galery_class=data.galery_class,
            )

        if isinstance(data, ImagesModel):
            return data

        raise NotImplementedError(f"Unknown data type: {data}")


class ImagesBlockExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(ImagesBlock, self.getConfigs())
