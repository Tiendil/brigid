import contextlib
import contextvars
import pathlib
from typing import Generator

import pydantic
from sentry_sdk import capture_message

from brigid.core.entities import BaseEntity
from brigid.library.entities import Article, Page


class RenderError(BaseEntity):
    filepath: pathlib.Path | None = None
    failed_text: str
    message: str


class RenderContext(BaseEntity):
    page: Page
    article: Article
    content: str | None = None
    renderer: int
    errors: list[RenderError] = pydantic.Field(default_factory=list)

    def add_error(self, failed_text: str, message: str) -> None:
        self.errors.append(RenderError(failed_text=failed_text, message=message, filepath=self.page.path))

    model_config = pydantic.ConfigDict(frozen=False)


render_context: contextvars.ContextVar[RenderContext] = contextvars.ContextVar("brigid_markdown_context")


@contextlib.contextmanager
def markdown_context(context: RenderContext) -> Generator[None, None, None]:

    token = render_context.set(context)

    try:
        yield
    finally:
        render_context.reset(token)

        prev_context = render_context.get(None)

        if prev_context is not None:
            prev_context.errors.extend(context.errors)

        if prev_context is None and context.errors:
            capture_message(repr(context.errors[0]))
