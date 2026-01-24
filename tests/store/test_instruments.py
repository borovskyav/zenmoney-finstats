from dataclasses import replace

import pytest

from finstats.container import Container
from finstats.store import InstrumentsRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def instruments_repository(container: Container) -> InstrumentsRepository:
    return container.resolve(InstrumentsRepository)


async def test_empty_db_get_all_should_return_empty_array(instruments_repository: InstrumentsRepository) -> None:
    assert await instruments_repository.get_instruments() == []


async def test_empty_db_get_many_should_return_empty_array(instruments_repository: InstrumentsRepository) -> None:
    assert await instruments_repository.get_instruments_by_id([x.id for x in testdata.TestInstruments]) == []


async def test_write_read_many_should_return_instruments(instruments_repository: InstrumentsRepository) -> None:
    await instruments_repository.save_instruments(testdata.TestInstruments)
    actual = await instruments_repository.get_instruments_by_id([x.id for x in testdata.TestInstruments])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestInstruments, key=lambda x: x.id)


async def test_get_all_should_return_ordered(instruments_repository: InstrumentsRepository) -> None:
    await instruments_repository.save_instruments(list(reversed(testdata.TestInstruments)))
    actual = await instruments_repository.get_instruments()
    assert actual == sorted(testdata.TestInstruments, key=lambda x: x.id)


async def test_update_should_return_updated(instruments_repository: InstrumentsRepository) -> None:
    await instruments_repository.save_instruments(testdata.TestInstruments)
    updated = replace(testdata.InstrumentUSD, rate=testdata.InstrumentUSD.rate + 1)
    await instruments_repository.save_instruments([updated])
    actual = await instruments_repository.get_instruments_by_id([testdata.InstrumentUSD.id])
    assert actual == [updated]


async def test_get_instruments_by_id_empty_input_returns_empty(instruments_repository: InstrumentsRepository) -> None:
    await instruments_repository.save_instruments(testdata.TestInstruments)
    assert await instruments_repository.get_instruments_by_id([]) == []


async def test_get_instruments_by_id_filters_unknown_ids(instruments_repository: InstrumentsRepository) -> None:
    await instruments_repository.save_instruments(testdata.TestInstruments)
    actual = await instruments_repository.get_instruments_by_id([testdata.InstrumentUSD.id, 999999])
    assert actual == [testdata.InstrumentUSD]


async def test_save_instruments_empty_noop(instruments_repository: InstrumentsRepository) -> None:
    await instruments_repository.save_instruments(testdata.TestInstruments)
    await instruments_repository.save_instruments([])
    actual = await instruments_repository.get_instruments_by_id([x.id for x in testdata.TestInstruments])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestInstruments, key=lambda x: x.id)
