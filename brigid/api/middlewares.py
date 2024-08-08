from typing import Any

import fastapi
from fastapi.responses import RedirectResponse
from sentry_sdk import capture_exception

from brigid.api import renderers
from brigid.api.utils import choose_language
from brigid.domain import request_context as d_request_context
from brigid.library.storage import storage


async def process_404(request, _):
    redirects = storage.get_redirects()

    original_path = request.url.path

    # normalize path

    if not original_path.startswith("/"):
        original_path = "/" + original_path

    if original_path[-1] == "/":
        original_path = original_path[:-1]

    if original_path in redirects.permanent:
        return RedirectResponse(redirects.permanent[original_path], status_code=301)

    language = choose_language(request)

    with d_request_context.init():
        d_request_context.set("storage", storage)
        return renderers.render_page(language, "404", status_code=404)


async def remove_double_slashes(request: fastapi.Request, call_next: Any):
    path = request.url.path

    if "//" not in path:
        return await call_next(request)

    while "//" in path:
        path = path.replace("//", "/")

    return RedirectResponse(path, status_code=301)


async def remove_trailing_slash(request: fastapi.Request, call_next: Any):
    path = request.url.path

    if path != "" and path != "/" and path[-1] == "/":
        return RedirectResponse(path[:-1], status_code=301)

    return await call_next(request)


async def set_content_language(request: fastapi.Request, call_next: Any):
    response = await call_next(request)

    if response.status_code != 200:
        return response

    if "content-language" in response.headers:
        return response

    path = request.url.path

    for language in storage.get_site().allowed_languages:
        if path.startswith(f"/{language}/") or path == f"/{language}":
            response.headers["content-language"] = language
            return response

    return response


async def process_expected_error(request, error):
    capture_exception(error)

    language = choose_language(request)

    with d_request_context.init():
        d_request_context.set("storage", storage)
        return renderers.render_page(language, "500", status_code=500)


async def request_context(request: fastapi.Request, call_next: Any):
    with d_request_context.init():
        d_request_context.set("storage", storage)
        return await call_next(request)
