import pathlib
from typing import Any

import pydantic
from pymdownx.blocks import BlocksExtension

from brigid.core.entities import BaseEntity
from brigid.domain.html import strip_html
from brigid.library.entities import Article
from brigid.renderer.context import render_context
from brigid.renderer.processors.toml_block import TomlBlock

# TODO: remove duplicated code


class ImageMixing:

    @pydantic.validator("alt")
    def escape_alt(cls, v):
        if v is None:
            return v

        return strip_html(v)


class Image(ImageMixing, BaseEntity):
    src: str
    alt: str | None = None

    # TODO: add caption to the image to show in the lightbox

    model_config = pydantic.ConfigDict(frozen=False)

    def url_file(self, article: Article) -> pathlib.Path:
        return article.path.parent / self.src


class ImagesModel(BaseEntity):
    caption: str | None = None
    images: list[Image]

    # TODO: rename to css_class
    galery_class: str | None = None

    model_config = pydantic.ConfigDict(frozen=False)

    @pydantic.validator("images")
    def minimum_1_image(cls, v):
        if len(v) < 1:
            raise ValueError("at least one image is required")
        return v

    @pydantic.model_validator(mode="after")
    def first_image_alt_from_caption(cls, self):

        if self.caption is not None and self.images[0].alt is None:
            self.images[0].alt = self.caption

        for image in self.images:
            if image.alt is None:
                raise ValueError("alt must be present")

        return self

    @pydantic.model_validator(mode="after")
    def default_galery_class(cls, self):
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
    def alt_or_caption(cls, self):
        if self.alt is None and self.caption is None:
            raise ValueError("alt or caption must be present")

        if self.alt is None and self.caption is not None:
            self.alt = self.caption

        return self


class ImagesBlock(TomlBlock):
    NAME = "brigid-images"
    models = ImageModel | ImagesModel
    root_tag = "figure"

    def root_css_classes(self, data: Any) -> list[str]:
        return ["brigid-images", data.galery_class]

    def process_data(self, data: Any) -> str:
        from brigid.theme.templates import render

        context = render_context.get()

        if isinstance(data, ImageModel):
            images = ImagesModel(
                caption=data.caption,
                images=[Image(src=data.src, alt=data.alt)],
                galery_class=data.galery_class,
            )
        else:
            images = data

        return render(
            "./blocks/images.html.j2",
            {
                "images": images,
                "article": context.article,
                "page": context.page,
            },
        )


class ImagesBlockExtension(BlocksExtension):

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(ImagesBlock, self.getConfigs())
