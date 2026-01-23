from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
import pytest_pg
import sqlalchemy as sa

from finstats.container import Container
from finstats.store import ConnectionScope, configure_container, run_migrations


@pytest.fixture(scope="session")
def pg_url_async(pg: pytest_pg.PG) -> str:
    return f"postgresql+asyncpg://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.database}"


@pytest.fixture(scope="session")
def pg_url_sync(pg: pytest_pg.PG) -> str:
    return f"postgresql+psycopg://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.database}"


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def container(pg_url_async: str) -> AsyncIterator[Container]:
    cont = Container()
    engine = configure_container(cont, pg_url_async)
    yield cont
    await engine.dispose()


@pytest.fixture(scope="session")
def connection(container: Container) -> ConnectionScope:
    return container.resolve(ConnectionScope)


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def migrate_database(connection: ConnectionScope, pg_url_sync: str) -> None:
    async with connection.acquire() as conn:
        await conn.execute(sa.text("DROP SCHEMA public CASCADE"))
        await conn.execute(sa.text("CREATE SCHEMA public"))
    run_migrations(pg_url_sync)
