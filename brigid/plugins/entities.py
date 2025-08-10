import pathlib

from brigid.core.entities import BaseEntity


class FileInfo(BaseEntity):
    sys_path: pathlib.Path
    url_path: str
    media_type: str

    @property
    def is_stylesheet(self) -> bool:
        return self.media_type == "text/css"

    @property
    def is_javascript(self) -> bool:
        return self.media_type == "application/javascript"
