from typing import Any

import fastapi
from fastapi.responses import RedirectResponse
from sentry_sdk import capture_exception

from brigid.api import renderers
from brigid.api.utils import choose_language
from brigid.domain import request_context as d_request_context
from brigid.domain.types import UrlPath
from brigid.domain.urls import add_base_path, mcp_url, root_url, strip_base_path
from brigid.library.storage import storage


def is_mcp_request(request: fastapi.Request) -> bool:
    path = UrlPath(request.url.path)
    mount_path = mcp_url().mount_path()
    return path == mount_path or path.startswith(f"{mount_path}/")


async def permanent_redirects(request: fastapi.Request, call_next: Any):
    redirects = storage.get_redirects()

    original_path = strip_base_path(UrlPath(request.url.path))

    original_path = UrlPath(f"/{original_path.rstrip('/')}")

    if original_path in redirects.permanent:
        target = redirects.permanent[original_path]

        if "://" in target:
            return RedirectResponse(target, status_code=301)

        if target.startswith("/"):
            return RedirectResponse(add_base_path(UrlPath(target)), status_code=301)

        raise ValueError(f"Redirect target must be absolute URL or root-relative path: {target}")

    return await call_next(request)


async def process_404(request, _):  # noqa: CCR001
    language = choose_language(request)

    with d_request_context.init():
        return renderers.render_page(language, "404", status_code=404)


async def remove_double_slashes(request: fastapi.Request, call_next: Any):
    path = UrlPath(request.url.path)

    if "//" not in path:
        return await call_next(request)

    while "//" in path:
        path = UrlPath(path.replace("//", "/"))

    return RedirectResponse(path, status_code=301)


async def root_to_language(request: fastapi.Request, call_next: Any):
    path = UrlPath(request.url.path)
    prefix = storage.get_site().url_path_prefix

    if path not in (prefix, f"{prefix}/"):
        return await call_next(request)

    language = choose_language(request)

    # TODO: show info to the user that language was chosen automatically
    return RedirectResponse(root_url(language=language).url(), status_code=302)


async def remove_trailing_slash(request: fastapi.Request, call_next: Any):

    if is_mcp_request(request):
        return await call_next(request)

    path = UrlPath(request.url.path)

    prefix = storage.get_site().url_path_prefix

    if path == prefix or path == f"{prefix}/" or path[-1] != "/":
        return await call_next(request)

    return RedirectResponse(UrlPath(path[:-1]), status_code=301)


async def set_content_language(request: fastapi.Request, call_next: Any):
    if is_mcp_request(request):
        return await call_next(request)

    response = await call_next(request)

    if response.status_code != 200:
        return response

    if "content-language" in response.headers:
        return response

    path = strip_base_path(UrlPath(request.url.path))

    for language in storage.get_site().allowed_languages:
        if path.startswith(f"{language}/") or path == language:
            response.headers["content-language"] = language
            return response

    return response


async def process_expected_error(request, error):
    capture_exception(error)

    language = choose_language(request)

    with d_request_context.init():
        return renderers.render_page(language, "500", status_code=500)


async def request_context(request: fastapi.Request, call_next: Any):
    with d_request_context.init():
        return await call_next(request)
