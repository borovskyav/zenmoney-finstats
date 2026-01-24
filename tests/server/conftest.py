from collections.abc import AsyncIterator

import pytest_asyncio
from aiohttp.test_utils import TestClient
from pytest_aiohttp import AiohttpClient

from finstats.application import Application
from finstats.container import Container
from finstats.zenmoney import ZenMoneyClient
from testing.testapp import TestApplication
from testing.zenmoney import FakeZenMoneyClient


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def zm_client(container: Container) -> FakeZenMoneyClient:
    client = FakeZenMoneyClient()
    container.register(service=ZenMoneyClient, instance=client)
    return client


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app(container: Container) -> Application:
    app = TestApplication(container)
    app.initialize()
    return app


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def client(aiohttp_client: AiohttpClient, app: Application) -> AsyncIterator[TestClient]:
    c = await aiohttp_client(app.app)
    yield c
    await c.close()


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def cleanup_fakes(zm_client: FakeZenMoneyClient) -> None:
    zm_client.cleanup()
