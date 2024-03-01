import pathlib
import shutil

from brigid.core import logging

logger = logging.get_module_logger()


class BaseCache:
    __slots__ = ()

    def initialize(self) -> None:
        raise NotImplementedError("initialize")

    def clear(self) -> None:
        raise NotImplementedError("clear")

    def set(self, cache_path: str, original_path) -> None:
        raise NotImplementedError("set")


class DummyCache(BaseCache):
    __slots__ = ()

    def initialize(self) -> None:
        pass

    def clear(self) -> None:
        pass

    def set(self, cache_path: str, original_path) -> None:
        pass


class FileCache(BaseCache):
    __slots__ = ("directory",)

    def __init__(self, directory: pathlib.Path) -> None:
        super().__init__()
        self.directory = directory

    def initialize(self) -> None:
        if not self.directory.exists():
            self.directory.mkdir(parents=True)

        self.clear()

    def clear(self) -> None:
        for entry in self.directory.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()

    def set(self, raw_cache_path: str, original_path: str) -> None:

        if raw_cache_path.startswith("/"):
            raw_cache_path = raw_cache_path[1:]

        cache_path = self.directory / raw_cache_path

        if not cache_path.parent.exists():
            try:
                cache_path.parent.mkdir(parents=True)
            except FileExistsError:
                logger.warning("cache_directory_created_in_parallel")

        shutil.copy(original_path, cache_path)


_cache: BaseCache = DummyCache()


def set_cache(cache: FileCache) -> None:
    cache.initialize()

    global _cache

    _cache = cache


def cache() -> BaseCache:
    assert _cache is not None
    return _cache
