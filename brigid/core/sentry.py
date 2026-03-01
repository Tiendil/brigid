from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from sentry_sdk import capture_exception as sentry_capture_exception
from sentry_sdk import init as initialize_sentry
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

import brigid

P = ParamSpec("P")
R = TypeVar("R")


def _is_enabled() -> bool:
    from brigid.application.settings import settings

    return settings.sentry.enabled


def capture(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if not _is_enabled():
            return func(*args, **kwargs)

        try:
            return func(*args, **kwargs)
        except Exception as error:
            sentry_capture_exception(error)
            raise

    return wrapper


def initialize(dsn: str, sample_rate: float, environment: str) -> None:
    initialize_sentry(
        dsn=dsn,
        sample_rate=sample_rate,
        traces_sample_rate=None,
        max_breadcrumbs=0,
        # Without this config Sentry miss important frames from stacktraces
        add_full_stack=True,
        attach_stacktrace=True,
        environment=environment,
        # set the correct project root directory
        project_root=brigid.__path__[0],
        # disable ALL automatically enabled integrations, because they periodically cause issues
        auto_enabling_integrations=False,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        disabled_integrations=[
            # disable default logging integration to use specialized structlog-sentry processor
            LoggingIntegration(event_level=None, level=None),
        ],
    )
