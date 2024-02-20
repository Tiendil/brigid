import asyncio

from brigid.application.application import with_app
from brigid.cli.application import app
from brigid.core import logging
from brigid.library.storage import storage
from brigid.renderer.markdown_render import render_page

logger = logging.get_module_logger()


def is_list_line(line: str) -> bool:
    if line.startswith("**"):
        return False

    line = line.lstrip()

    return line.startswith("-") or line.startswith("*") or line.startswith("+")


def is_line_empty(line: str) -> bool:
    return not line.strip()


# TODO: what with nested lists?
# TODO: what with numbered lists?
# TODO: make difference for different list types (-, *, +, digit)
def parser(text: str) -> bool:  # noqa: CCR001

    is_in_list = False

    can_has_problem = False

    for line in text.split("\n"):
        if is_list_line(line):
            if can_has_problem:
                return True

            is_in_list = True
            continue

        if is_line_empty(line) and is_in_list:
            can_has_problem = True
            continue

        is_in_list = False
        can_has_problem = False

    return False


async def run() -> None:
    errors = []

    async with with_app():
        # pages are loaded on the application initialization

        site = storage.get_site()

        for page in storage.all_pages():
            context = render_page(page=page)

            if parser(page.body):
                context.add_error("test is unknown", "the page has separated list items")

            errors.extend(context.errors)

        article_404 = storage.get_article(slug="404")

        if set(article_404.pages) != set(site.allowed_languages):
            raise ValueError("404 article pages are not consistent with site allowed languages")

        article_500 = storage.get_article(slug="500")

        if set(article_500.pages) != set(site.allowed_languages):
            raise ValueError("500 article pages are not consistent with site allowed languages")

    if not errors:
        logger.info("everything_is_ok")
        return

    for error in errors:
        logger.error(
            "markdown_render_error",
            filepath=str(error.filepath),
            failed_text=error.failed_text,
            message=error.message,
        )

    logger.error("markdown_render_errors", errors_number=len(errors))


@app.command()
def validate() -> None:
    asyncio.run(run())
