from brigid.library.entities import Page
from brigid.renderer.markdown_render import render_page
from brigid.validation.entities import Error


def page_is_rendered(page: Page) -> list[Error]:
    context = render_page(page=page)

    errors = []

    for error in context.errors:
        errors.append(Error(filepath=page.path, message=f'Render error "{error.message}" in "{error.failed_text}"'))

    return errors
