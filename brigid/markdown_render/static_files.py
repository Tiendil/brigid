import pathlib

from PIL import Image, UnidentifiedImageError

from brigid.core.entities import BaseEntity


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

        try:
            with Image.open(path) as img:
                width, height = img.size
        except UnidentifiedImageError:
            width, height = 0, 0

        self._images[path] = ImageInfo(path=path, width=width, height=height)

        return self._images[path]


files = FilesInfo()
