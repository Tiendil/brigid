import contextlib
import pathlib
from typing import Generator

from brigid.core import logging
from brigid.library.discovering import load_article, load_page
from brigid.library.storage import storage
from watchdog import events
from watchdog.observers import Observer


_observer = None


logger = logging.get_module_logger()


class EventHandler(events.FileSystemEventHandler):
    def on_any_event(self, event):

        path = pathlib.Path(event.src_path).resolve().absolute()

        # TODO: parametrize
        if any(path.name.startswith(ext) for ext in (".",)):
            return

        # TODO: parametrize
        if any(path.name.endswith(ext) for ext in ("~",)):
            return

        if isinstance(event, events.FileModifiedEvent):

            if path.name.endswith(".md"):
                page = load_page(path)
                storage.add_page(page, replace=True)
                logger.info("page_updated", path=page.path)
                return

            if path.name == "article.toml":
                article = load_article(path)
                storage.add_article(article, replace=True)
                logger.info("article_updated", article=article.path)
                return

            # TODO: update site
            # TODO: update images storage
            # TODO: update redirects

            return

        # TODO: on file create
        # TODO: on file delete


def observer():
    global _observer

    if _observer is None:
        _observer = Observer()

    return _observer


@contextlib.contextmanager
def observe_storage(directory: pathlib.Path) -> Generator[None, None, None]:
    logger.info("enable_storage_observer")

    observer().schedule(EventHandler(), directory.absolute(), recursive=True)
    observer().start()

    logger.info("storage_observer_started")

    try:
        yield
    finally:
        observer().stop()
        observer().join()

        logger.info("storage_observer_stopped")
