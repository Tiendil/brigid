import contextlib
import os
from typing import AsyncGenerator

import fastapi
from fastapi.middleware.cors import CORSMiddleware

from brigid.api import http_handlers as api_http_handlers
from brigid.api import middlewares as api_middlewares
from brigid.api import static_cache as api_static_cache
from brigid.api.settings import settings as api_settings
from brigid.application.settings import settings
from brigid.core import logging, sentry
from brigid.library import discovering
from brigid.library.settings import settings as library_settings
from brigid.library.storage import storage
from brigid.mcp.server import create_mcp

logger = logging.get_module_logger()


def initialize_api(app: fastapi.FastAPI) -> None:
    logger.info("initialize_api")

    prefix = storage.get_site().url_path_prefix
    app.include_router(api_http_handlers.router, prefix=prefix)

    app.middleware("http")(api_middlewares.set_content_language)
    app.middleware("http")(api_middlewares.permanent_redirects)
    app.middleware("http")(api_middlewares.remove_trailing_slash)
    app.middleware("http")(api_middlewares.root_to_language)
    app.middleware("http")(api_middlewares.remove_double_slashes)
    app.middleware("http")(api_middlewares.request_context)

    app.exception_handler(404)(api_middlewares.process_404)
    app.exception_handler(Exception)(api_middlewares.process_expected_error)

    logger.info("api_initialized")


def initialize_sentry() -> None:
    if not settings.sentry.enabled:
        return

    logger.info("sentry_enabled")

    sentry.initialize(
        dsn=settings.sentry.dsn,
        sample_rate=settings.sentry.sample_rate,
        environment=settings.environment,
    )

    logger.info("sentry_initialized")


@sentry.capture
def initialize_cache() -> None:
    if not api_settings.cache_directory:
        return

    cache = api_static_cache.FileCache(directory=api_settings.cache_directory)
    api_static_cache.set_cache(cache)


@sentry.capture
def initialize_content() -> None:
    discovering.load(directory=library_settings.directory)


def create_app() -> fastapi.FastAPI:  # noqa: CCR001
    logging.initialize(use_sentry=settings.sentry.enabled)

    logger.info("create_app")

    initialize_sentry()
    initialize_cache()
    initialize_content()

    @contextlib.asynccontextmanager
    async def lifespan(app: fastapi.FastAPI) -> AsyncGenerator[None, None]:
        async with contextlib.AsyncExitStack() as stack:
            mcp_app = create_mcp(app)

            await app.router.startup()

            # There is a strange bug in fastmcp/mcp/anyio with lifespan context
            # `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`
            # so, we turn off MCP server during tests, for now
            # TODO: try to fix it properly later
            if not os.environ.get("BRIGID_TESTS_RUNNING"):
                await stack.enter_async_context(mcp_app.lifespan(app))

            yield

            await app.router.shutdown()

    app = fastapi.FastAPI(
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        redirect_slashes=False,
    )

    initialize_api(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=False,
        allow_methods=[],
        allow_headers=[],
    )

    logger.info("app_created")

    return app


@contextlib.asynccontextmanager
async def with_app() -> AsyncGenerator[fastapi.FastAPI, None]:
    app = create_app()
    async with app.router.lifespan_context(app):
        yield app
