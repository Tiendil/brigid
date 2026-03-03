import asyncio
import os
from typing import AsyncGenerator, Generator

import fastapi
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from brigid.domain import request_context
from brigid.library.tests.fixtures import *  # noqa


@pytest.fixture(scope="session", autouse=True)
def mark_tests_running() -> None:
    os.environ["BRIGID_TESTS_RUNNING"] = "True"
    os.environ.setdefault("BRIGID_LIBRARY_DIRECTORY", "./test-content")


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> Generator[asyncio.AbstractEventLoop, asyncio.AbstractEventLoop, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_request_context():
    with request_context.init():
        yield


@pytest_asyncio.fixture(scope="session", autouse=True)
async def app(mark_tests_running) -> AsyncGenerator[fastapi.FastAPI, None]:
    # we want to guarantie that there will be no hidden initializations
    # of applications or settings => we import application module in the fixture
    from brigid.application import application

    async with application.with_app() as app:
        yield app


@pytest.fixture
def client(app: fastapi.FastAPI) -> Generator[TestClient, None, None]:
    yield TestClient(app, raise_server_exceptions=True, follow_redirects=False)
