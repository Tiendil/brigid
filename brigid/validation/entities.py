import pathlib

from brigid.core.entities import BaseEntity


class Error(BaseEntity):
    filepath: pathlib.Path | None
    message: str
