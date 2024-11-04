from brigid.library.entities import Page, PageSeriesInfo
from brigid.library.storage import storage


def get_page_series_info(original_page: Page) -> PageSeriesInfo:

    if original_page.series is None:
        raise NotImplementedError("Only pages with series are supported")

    series_pages: list[str] = []

    for page in storage.get_posts(language=original_page.language):
        if original_page.series != page.series:
            continue

        series_pages.append(page.id)

    series_pages.sort(key=lambda p_id: storage.get_page(p_id).published_at)

    first_page = series_pages[0]
    prev_page = None
    next_page = None

    original_page_index = series_pages.index(original_page.id)

    if original_page_index > 0:
        prev_page = series_pages[original_page_index - 1]

    if original_page_index < len(series_pages) - 1:
        next_page = series_pages[original_page_index + 1]

    return PageSeriesInfo(
        first_page=first_page,
        prev_page=prev_page,
        next_page=next_page,
    )
