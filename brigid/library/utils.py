from brigid.domain.text import capitalize_first
from brigid.library.entities import Page
from brigid.library.storage import storage


def page_title(page: Page, short: bool) -> str:

    if short:
        return capitalize_first(page.title)

    if page.series:
        series_title = storage.get_site().languages[page.language].tags_translations[page.series]
        return f"{capitalize_first(series_title)}: {capitalize_first(page.title)}"

    return capitalize_first(page.title)
