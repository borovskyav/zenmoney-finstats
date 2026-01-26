import pytest

from client.client import FinstatsClient
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_merchants_should_return_all_merchants(client: FinstatsClient) -> None:
    merchants = await client.get_merchants()
    assert len(merchants) == len(testdata.TestMerchants)
    expected_sorted = sorted(merchants, key=lambda x: x.id)
    actual_sorted = sorted(testdata.TestMerchants, key=lambda x: x.id)
    for i, expected_merchant in enumerate(expected_sorted):
        assert actual_sorted[i].id == expected_merchant.id
        assert actual_sorted[i].title == expected_merchant.title
        assert actual_sorted[i].changed == expected_merchant.changed
        assert actual_sorted[i].user == expected_merchant.user
