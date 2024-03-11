import asyncio

from brigid.application.application import with_app
from brigid.cli.application import app
from brigid.core import logging
from brigid.validation import validators

logger = logging.get_module_logger()


async def run() -> None:
    async with with_app():
        # pages are loaded on the application initialization
        errors = validators.validate()

    if not errors:
        logger.info("everything_is_ok")
        return

    for error in errors:
        logger.error(
            "markdown_render_error",
            filepath=str(error.filepath),
            message=error.message,
        )

    logger.error("markdown_render_errors", errors_number=len(errors))


@app.command()
def validate() -> None:
    asyncio.run(run())
