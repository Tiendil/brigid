import os
import pathlib
from typing import Any

import jinja2

from brigid.core import logging
from brigid.jinja2_render.templates import get_jinjaglobals
from brigid.plugins.entities import FileInfo
from brigid.plugins.plugin import Plugin
from brigid.plugins.theme import jinjaglobals
from brigid.plugins.theme.settings import settings

logger = logging.get_module_logger()


class ThemePlugin(Plugin):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self._static_files_map = {}
        self._discover_static_files()

    def _discover_static_files(self) -> None:  # noqa: CCR001
        for path in [self.settings.static_redefined, self.settings.static_base]:
            if path is None:
                continue

            if not pathlib.Path(path).exists():
                logger.warning("static_path_not_found", path=path, plugin=self.slug)
                continue

            for root, _, files in os.walk(path):
                for file in files:
                    extension = file.split(".")[-1].lower()

                    if extension not in self.settings.static_extensions:
                        continue

                    media_type = self.settings.static_extensions[extension]

                    file_path = pathlib.Path(root) / file

                    url_path = str(pathlib.Path(file_path.relative_to(path)))

                    if file in self._static_files_map:
                        continue

                    self._static_files_map[file] = FileInfo(
                        sys_path=file_path, url_path=url_path, media_type=media_type
                    )

    def jinjaglobals(self) -> tuple[dict[str, Any], dict[str, Any]]:
        return get_jinjaglobals(jinjaglobals)

    def templates_loader(self) -> jinja2.BaseLoader:
        loaders = []

        if settings.templates_redefined:
            loaders.append(jinja2.FileSystemLoader(settings.templates_redefined, followlinks=True))

        loaders.append(jinja2.FileSystemLoader(settings.templates_base, followlinks=True))

        return jinja2.ChoiceLoader(loaders)

    def static_file_info(self, filename: str) -> FileInfo | None:
        return self._static_files_map.get(filename)

    def static_files(self) -> list[FileInfo]:
        return list(self._static_files_map.values())


plugin = ThemePlugin(slug="theme", settings=settings)
