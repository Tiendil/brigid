import contextlib
import contextvars
import enum
from typing import Any, TypedDict

# TODO: these imports may cause circular dependencies, fix them
from brigid.domain.urls import UrlsBase
from brigid.library.storage import Storage


class Variable(enum.StrEnum):
    language = "language"
    url = "url"
    storage = "storage"


class RequestContextType(TypedDict):
    language: str
    url: UrlsBase
    storage: Storage


request_context: contextvars.ContextVar[RequestContextType] = contextvars.ContextVar("request_context")


@contextlib.contextmanager
def init():
    token = request_context.set({})

    try:
        yield
    finally:
        request_context.reset(token)


def set(name: str, value: Any):
    if name not in Variable:
        raise NotImplementedError(f"Variable {name} is not supported")

    context = request_context.get()

    if name in context:
        raise NotImplementedError(f"Variable {name} is already set in the request context")

    context[name] = value  # type: ignore


def get(name: str) -> Any:
    if name not in Variable:
        raise NotImplementedError(f"Variable {name} is not supported")

    context = request_context.get()

    if name not in context:
        raise NotImplementedError(f"Variable {name} is not set in the request context")

    return context[name]  # type: ignore


def current() -> RequestContextType:
    return request_context.get()
