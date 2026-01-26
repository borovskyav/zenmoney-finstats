import pytest

from client.client import FinstatsClient
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_instruments_should_return_all_instruments(client: FinstatsClient) -> None:
    instruments = await client.get_instruments()
    assert len(instruments) == len(testdata.TestInstruments)
    expected_sorted = sorted(instruments, key=lambda x: x.id)
    actual_sorted = sorted(testdata.TestInstruments, key=lambda x: x.id)
    for i, expected_instrument in enumerate(expected_sorted):
        assert actual_sorted[i].id == expected_instrument.id
        assert actual_sorted[i].title == expected_instrument.title
        assert actual_sorted[i].short_title == expected_instrument.short_title
        assert actual_sorted[i].symbol == expected_instrument.symbol
        assert actual_sorted[i].rate == expected_instrument.rate
        assert actual_sorted[i].changed == expected_instrument.changed
