import pathlib
from typing import Callable

from brigid.core.entities import BaseEntity
from brigid.library.entities import Article, Page
from brigid.library.storage import storage
from brigid.renderer.markdown_render import render_page
from brigid.validation.entities import Error
from brigid.validation.global_validators import required_article
from brigid.validation.lists_formatting import page_has_correct_list_formatting


def page_is_rendered(page: Page) -> list[Error]:
    context = render_page(page=page)

    errors = []

    for error in context.errors:
        errors.append(Error(filepath=page.path,
                            message=f'Render error "{error.message}" in "{error.failed_text}"'))

    return errors
