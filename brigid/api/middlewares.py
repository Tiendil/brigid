import uuid
from collections import Counter
from importlib import metadata
from typing import Any, Iterable

import fastapi
from brigid.api import renderers
from brigid.api.utils import choose_language
from brigid.core import errors, logging
from brigid.domain.urls import UrlsRoot
from brigid.library.settings import settings as library_settings
from brigid.library.similarity import get_similar_pages
from brigid.library.storage import storage
from brigid.theme.templates import render
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from sentry_sdk import capture_exception
from starlette.exceptions import HTTPException as StarletteHTTPException


async def process_404(request, error):
    redirects = storage.get_redirects()

    original_path = request.url.path

    # normalize path

    if not original_path.startswith('/'):
        original_path = '/' + original_path

    if original_path[-1] == '/':
        original_path = original_path[:-1]

    if original_path in redirects.permanent:
        return RedirectResponse(redirects.permanent[original_path], status_code=301)

    language = choose_language(request)

    # captute all unprocessed 404 errors
    capture_exception(error)

    return renderers.render_page(language, '404', status_code=404)


async def remove_double_slashes(request: fastapi.Request, call_next: Any):
    path = request.url.path

    if '//' not in path:
        return await call_next(request)

    while '//' in path:
        path = path.replace('//', '/')

    return RedirectResponse(path, status_code=301)


async def remove_trailing_slash(request: fastapi.Request, call_next: Any):
    path = request.url.path

    if path != '/' and path[-1] == '/':
        return RedirectResponse(path[:-1], status_code=301)

    return await call_next(request)


async def set_content_language(request: fastapi.Request, call_next: Any):
    response = await call_next(request)

    if response.status_code != 200:
        return response

    if 'content-language' in response.headers:
        return response

    path = request.url.path

    for language in storage.get_site().allowed_languages:
        if path.startswith(f'/{language}/') or path == f'/{language}':
            response.headers['content-language'] = language
            return response

    return response


async def process_expected_error(request, error):
    capture_exception(error)

    language = choose_language(request)

    return renderers.render_page(language, '500', status_code=500)
