import contextlib
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

logger = logging.get_module_logger()


def initialize_api(app: fastapi.FastAPI) -> None:
    logger.info("initialize_api")

    app.include_router(api_http_handlers.router)

    app.middleware("http")(api_middlewares.request_context)
    app.middleware("http")(api_middlewares.remove_double_slashes)
    app.middleware("http")(api_middlewares.remove_trailing_slash)
    app.middleware("http")(api_middlewares.set_content_language)

    app.exception_handler(404)(api_middlewares.process_404)
    app.exception_handler(Exception)(api_middlewares.process_expected_error)

    if api_settings.cache_directory:
        cache = api_static_cache.FileCache(directory=api_settings.cache_directory)
        api_static_cache.set_cache(cache)

    logger.info("api_initialized")


@contextlib.asynccontextmanager
async def use_sentry() -> AsyncGenerator[None, None]:
    logger.info("sentry_enabled")

    sentry.initialize(
        dsn=settings.sentry.dsn,
        enable_tracing=settings.sentry.enable_tracing,
        sample_rate=settings.sentry.sample_rate,
        traces_sample_rate=settings.sentry.traces_sample_rate,
        environment=settings.environment,
    )

    logger.info("sentry_initialized")

    yield

    logger.info("sentry_disabled")


def create_app() -> fastapi.FastAPI:  # noqa: CCR001
    logging.initialize(use_sentry=settings.sentry.enabled)

    logger.info("create_app")

    @contextlib.asynccontextmanager
    async def lifespan(app: fastapi.FastAPI) -> AsyncGenerator[None, None]:
        async with contextlib.AsyncExitStack() as stack:
            if settings.sentry.enabled:
                await stack.enter_async_context(use_sentry())

            await app.router.startup()

            # TODO: must be skipped in tests?
            discovering.load(directory=library_settings.directory)

            yield

            await app.router.shutdown()

    app = fastapi.FastAPI(
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
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
    async with app.router.lifespan_context(app):
        yield app


app = create_app()
