import pytest_asyncio

from finstats.container import Container
from finstats.zenmoney import ZenMoneyClient


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def container(container: Container) -> Container:
    container.register(ZenMoneyClient)
    return container
