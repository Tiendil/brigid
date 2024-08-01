import contextlib
import contextvars
import enum


class Variable(enum.StrEnum):
    language = "language"
    url = "url"
    site = "site"


request_context = contextvars.ContextVar("request_context")


@contextlib.contextmanager
def init():
    token = request_context.set({})

    try:
        yield
    finally:
        request_context.reset(token)


def set(name: str, value: str):
    if name not in Variable:
        raise NotImplementedError(f"Variable {name} is not supported")

    context = request_context.get()

    if name in context:
        raise NotImplementedError(f"Variable {name} is already set in the request context")

    context[name] = value


def get(name: str) -> str:
    if name not in Variable:
        raise NotImplementedError(f"Variable {name} is not supported")

    context = request_context.get()

    if name not in context:
        raise NotImplementedError(f"Variable {name} is not set in the request context")

    return context[name]


def current() -> dict:
    return request_context.get()
