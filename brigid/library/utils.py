from brigid.library.entities import Page
from brigid.library.storage import storage


def page_title(page: Page, short: bool) -> str:

    if short:
        return page.title.capitalize()

    if page.series:
        series_title = storage.get_site().languages[page.language].tags_translations[page.series]
        return f"{series_title.capitalize()}: {page.title.capitalize()}"

    return page.title.capitalize()
