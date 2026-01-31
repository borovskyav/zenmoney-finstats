from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from pytest_aiohttp import AiohttpClient

from client.client import FinstatsClient
from finstats.application import Application
from finstats.container import Container
from finstats.store import AccountsRepository, InstrumentsRepository, MerchantsRepository, TagsRepository, TransactionsRepository
from finstats.zenmoney import ZenMoneyClient
from testing import testdata
from testing.testapp import TestApplication
from testing.zenmoney import FakeZenMoneyClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


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
async def client(aiohttp_client: AiohttpClient, app: Application) -> AsyncIterator[FinstatsClient]:
    c = await aiohttp_client(app.app)
    yield FinstatsClient(c.session, c.make_url("/"), token="ok")
    await c.close()


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def cleanup_fakes(zm_client: FakeZenMoneyClient) -> None:
    zm_client.cleanup()


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def fake_data(container: Container) -> None:
    await container.resolve(TransactionsRepository).save_transactions(testdata.TestTransactions)
    await container.resolve(MerchantsRepository).save_merchants(testdata.TestMerchants)
    await container.resolve(InstrumentsRepository).save_instruments(testdata.TestInstruments)
    await container.resolve(TagsRepository).save_tags(testdata.TestTags)
    await container.resolve(AccountsRepository).save_accounts(testdata.TestAccounts + [testdata.ArchivedCashAccount, testdata.ArchivedDebtAccount])


async def test_health_should_return_ok(client: FinstatsClient) -> None:
    assert await client.health()
