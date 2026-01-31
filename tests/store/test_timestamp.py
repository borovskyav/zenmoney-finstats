import pytest

from finstats.container import Container
from finstats.store import TimestampRepository

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def timestamp_repository(container: Container) -> TimestampRepository:
    return container.resolve(TimestampRepository)


async def test_empty_db_get_timestamp_should_be_0(timestamp_repository: TimestampRepository) -> None:
    ts = await timestamp_repository.get_last_timestamp()
    assert ts == 0


async def test_update_timestamp_and_read_should_return_timestamp(timestamp_repository: TimestampRepository) -> None:
    await timestamp_repository.save_last_timestamp(123456789)
    ts = await timestamp_repository.get_last_timestamp()
    assert ts == 123456789


async def test_rewrite_timestamp_should_be_rewritten(timestamp_repository: TimestampRepository) -> None:
    await timestamp_repository.save_last_timestamp(123456789)
    ts = await timestamp_repository.get_last_timestamp()
    assert ts == 123456789

    await timestamp_repository.save_last_timestamp(123456790)
    ts = await timestamp_repository.get_last_timestamp()
    assert ts == 123456790
