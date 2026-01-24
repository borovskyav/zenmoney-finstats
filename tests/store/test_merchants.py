import uuid
from dataclasses import replace

import pytest

from finstats.container import Container
from finstats.store import MerchantsRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def merchant_repository(container: Container) -> MerchantsRepository:
    return container.resolve(MerchantsRepository)


async def test_empty_db_get_one_should_return_none(merchant_repository: MerchantsRepository) -> None:
    assert await merchant_repository.get_merchant_by_id(testdata.MerchantQuadCode.id) is None


async def test_empty_db_get_many_should_return_empty_array(merchant_repository: MerchantsRepository) -> None:
    assert await merchant_repository.get_merchants_by_id([x.id for x in testdata.TestMerchants]) == []


async def test_empty_db_get_all_should_return_empty_array(merchant_repository: MerchantsRepository) -> None:
    assert await merchant_repository.get_merchants() == []


async def test_write_read_should_return_merchant(merchant_repository: MerchantsRepository) -> None:
    await merchant_repository.save_merchants(testdata.TestMerchants)
    actual = await merchant_repository.get_merchant_by_id(testdata.MerchantQuadCode.id)
    assert actual == testdata.MerchantQuadCode


async def test_write_read_many_should_return_merchants(merchant_repository: MerchantsRepository) -> None:
    await merchant_repository.save_merchants(testdata.TestMerchants)
    actual = await merchant_repository.get_merchants_by_id([x.id for x in testdata.TestMerchants])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestMerchants, key=lambda x: x.id)


async def test_get_all_should_return_merchants(merchant_repository: MerchantsRepository) -> None:
    await merchant_repository.save_merchants(testdata.TestMerchants)
    actual = await merchant_repository.get_merchants()
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestMerchants, key=lambda x: x.id)


async def test_update_should_return_updated(merchant_repository: MerchantsRepository) -> None:
    await merchant_repository.save_merchants(testdata.TestMerchants)
    updated = replace(testdata.MerchantQuadCode, title="QuadCode Cyprus")
    await merchant_repository.save_merchants([updated])
    actual = await merchant_repository.get_merchant_by_id(testdata.MerchantQuadCode.id)
    assert actual == updated


async def test_get_merchants_by_id_empty_input_returns_empty(merchant_repository: MerchantsRepository) -> None:
    await merchant_repository.save_merchants(testdata.TestMerchants)
    assert await merchant_repository.get_merchants_by_id([]) == []


async def test_get_merchants_by_id_filters_unknown_ids(merchant_repository: MerchantsRepository) -> None:
    await merchant_repository.save_merchants(testdata.TestMerchants)
    actual = await merchant_repository.get_merchants_by_id([testdata.MerchantQuadCode.id, uuid.uuid4()])
    assert actual == [testdata.MerchantQuadCode]


async def test_save_merchants_empty_noop(merchant_repository: MerchantsRepository) -> None:
    await merchant_repository.save_merchants(testdata.TestMerchants)
    await merchant_repository.save_merchants([])
    actual = await merchant_repository.get_merchants_by_id([x.id for x in testdata.TestMerchants])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestMerchants, key=lambda x: x.id)
