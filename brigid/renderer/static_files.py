import pathlib

from brigid.core.entities import BaseEntity
from PIL import Image


class ImageInfo(BaseEntity):
    path: pathlib.Path
    width: int
    height: int


class FilesInfo:
    __slots__ = ("_images",)

    def __init__(self) -> None:
        self._images: dict[pathlib.Path, ImageInfo] = {}

    def image_info(self, path: pathlib.Path) -> ImageInfo:
        if path in self._images:
            return self._images[path]

        with Image.open(path) as img:
            width, height = img.size

        self._images[path] = ImageInfo(path=path, width=width, height=height)

        return self._images[path]


files = FilesInfo()
