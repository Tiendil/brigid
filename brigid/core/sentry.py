from sentry_sdk import init as initialize_sentry
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

import brigid


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
