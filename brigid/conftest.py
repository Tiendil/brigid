import asyncio
import os
from typing import AsyncGenerator, Generator

import fastapi
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from brigid.application import application
from brigid.domain import request_context
from brigid.library.storage import storage


@pytest.fixture(scope="session", autouse=True)
def mark_tests_running():
    os.environ["BRIGID_TESTS_RUNNING"] = "True"


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> Generator[asyncio.AbstractEventLoop, asyncio.AbstractEventLoop, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_request_context():
    with request_context.init():
        request_context.set("storage", storage)
        yield


@pytest_asyncio.fixture(scope="session", autouse=True)
async def app() -> AsyncGenerator[fastapi.FastAPI, None]:
    async with application.with_app() as app:
        yield app


@pytest.fixture
def client(app: fastapi.FastAPI) -> Generator[TestClient, None, None]:
    yield TestClient(app, raise_server_exceptions=True, follow_redirects=False)
