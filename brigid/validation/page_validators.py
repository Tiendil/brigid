from brigid.library.entities import Page
from brigid.library.storage import storage
from brigid.renderer.markdown_render import render_page
from brigid.validation.entities import Error


def page_is_rendered(page: Page) -> list[Error]:
    context = render_page(page=page)

    errors = []

    for error in context.errors:
        errors.append(Error(filepath=page.path, message=f'Render error "{error.message}" in "{error.failed_text}"'))

    return errors


def page_has_correct_tags(page: Page) -> list[Error]:
    errors = []

    allowed_tags = set(storage.get_site().languages[page.language].tags_translations.keys())

    for tag in page.tags:
        if tag not in allowed_tags:
            errors.append(
                Error(filepath=page.path, message=f"Tag {tag} is not registered for site language {page.language}")
            )

    return errors


def page_has_correct_series_tags(page: Page) -> list[Error]:
    if page.series is None:
        return []

    errors = []

    allowed_series_tags = set(storage.get_site().languages[page.language].tags_translations.keys())

    if page.series not in page.tags:
        errors.append(Error(filepath=page.path, message=f"Series tag {page.series} should be also in page tags"))

    if page.series not in allowed_series_tags:
        errors.append(
            Error(
                filepath=page.path,
                message=f"Series tag {page.series} is not registered for site language {page.language}",
            )
        )

    return errors
