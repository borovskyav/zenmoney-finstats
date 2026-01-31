import uuid
from dataclasses import replace

import pytest

from finstats.container import Container
from finstats.store import AccountsRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def accounts_repository(container: Container) -> AccountsRepository:
    return container.resolve(AccountsRepository)


async def test_empty_db_get_one_should_return_none(accounts_repository: AccountsRepository) -> None:
    assert await accounts_repository.get_account(testdata.CashAccount.id) is None


async def test_empty_db_get_many_should_return_empty_array(accounts_repository: AccountsRepository) -> None:
    assert await accounts_repository.get_accounts_by_id([x.id for x in testdata.TestAccounts]) == []


async def test_write_read_should_return_account(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    actual = await accounts_repository.get_account(testdata.CashAccount.id)
    assert actual == testdata.CashAccount


async def test_write_read_many_should_return_accounts(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    actual = await accounts_repository.get_accounts_by_id([x.id for x in testdata.TestAccounts])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestAccounts, key=lambda x: x.id)


async def test_update_should_return_updated(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    updated = replace(testdata.CashAccount, title="Cash Box", balance=testdata.CashAccount.balance + 1)
    await accounts_repository.save_accounts([updated])
    actual = await accounts_repository.get_account(testdata.CashAccount.id)
    assert actual == updated


async def test_get_accounts_by_id_with_empty_input_should_return_empty(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    assert await accounts_repository.get_accounts_by_id([]) == []


async def test_get_accounts_by_id_with_unknown_ids_should_filter(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    actual = await accounts_repository.get_accounts_by_id([testdata.CashAccount.id, uuid.uuid4()])
    assert actual == [testdata.CashAccount]


async def test_save_accounts_with_empty_input_should_do_nothing(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await accounts_repository.save_accounts([])
    actual = await accounts_repository.get_accounts_by_id([x.id for x in testdata.TestAccounts])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestAccounts, key=lambda x: x.id)


async def test_find_accounts_by_default_should_exclude_debts(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts + [testdata.ArchivedCashAccount])
    actual = await accounts_repository.find_accounts()
    expected = [x for x in testdata.TestAccounts if x.type != "debt"]
    assert sorted(actual, key=lambda x: x.id) == sorted(expected, key=lambda x: x.id)


async def test_find_accounts_with_show_debts_should_include_debts(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    actual = await accounts_repository.find_accounts(show_debts=True)
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestAccounts, key=lambda x: x.id)


async def test_find_accounts_with_show_archive_should_return_archived(accounts_repository: AccountsRepository) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts + [testdata.ArchivedCashAccount])
    actual = await accounts_repository.find_accounts(show_archive=True)
    assert actual == [testdata.ArchivedCashAccount]


async def test_find_accounts_with_archive_and_debts_should_return_archived_debts(
    accounts_repository: AccountsRepository,
) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts + [testdata.ArchivedDebtAccount, testdata.ArchivedCashAccount])
    actual = await accounts_repository.find_accounts(show_archive=True, show_debts=True)
    assert sorted(actual, key=lambda x: x.id) == sorted(
        [testdata.ArchivedDebtAccount, testdata.ArchivedCashAccount],
        key=lambda x: x.id,
    )
