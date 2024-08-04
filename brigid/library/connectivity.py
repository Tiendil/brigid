from collections import defaultdict

from brigid.domain import request_context
from brigid.library.storage import storage
from brigid.renderer.markdown_render import render_page


class Connectivity:
    __slots__ = ("_connections", "_reverse_connections", "_processed_pages")

    def __init__(self) -> None:
        self._processed_pages: set[str] = set()
        self._connections: dict[str, set[str]] = defaultdict(set)
        self._reverse_connections: dict[str, set[str]] = defaultdict(set)

    def get_referenced_to(self, page_id: str) -> set[str]:
        return self._connections[page_id]

    def get_referenced_from(self, page_id: str) -> set[str]:
        return self._reverse_connections[page_id]

    def add_connection(self, target_page_id: str, reference_page_id: str):
        self._connections[reference_page_id].add(target_page_id)
        self._reverse_connections[target_page_id].add(reference_page_id)

    def process_page(self, page_id: str) -> None:
        if page_id in self._processed_pages:
            return

        with request_context.init():
            request_context.set("storage", storage)
            render_page(storage.get_page(page_id))

        self._processed_pages.add(page_id)

    def initialize(self) -> None:
        for language in storage.get_site().allowed_languages:
            for page in storage.get_posts(language=language):
                if page.id not in self._processed_pages:
                    self.process_page(page.id)


connectivity = Connectivity()
