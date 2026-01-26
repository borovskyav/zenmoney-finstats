import pytest

from client import AccountModel
from client.client import FinstatsClient
from finstats.domain import Account
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_accounts_by_default_should_exclude_debts(client: FinstatsClient) -> None:
    actual = await client.get_accounts()
    expected = [x for x in testdata.TestAccounts if x.type != "debt"]
    assert len(actual) == len(expected)

    actual_sorted = sorted(actual, key=lambda x: x.id)
    expected_sorted = sorted(expected, key=lambda x: x.id)
    for i, actual_account in enumerate(actual_sorted):
        _assert_account_matches(expected_sorted[i], actual_account)


async def test_get_accounts_should_return_all_accounts(client: FinstatsClient) -> None:
    actual = await client.get_accounts(show_debts=True)
    assert len(actual) == len(testdata.TestAccounts)

    actual_sorted = sorted(actual, key=lambda x: x.id)
    expected_sorted = sorted(testdata.TestAccounts, key=lambda x: x.id)
    for i, actual_account in enumerate(actual_sorted):
        _assert_account_matches(expected_sorted[i], actual_account)


async def test_get_accounts_with_show_archive_should_return_archived(client: FinstatsClient) -> None:
    accounts = await client.get_accounts(show_archive=True)
    assert len(accounts) == 1

    _assert_account_matches(testdata.ArchivedCashAccount, accounts[0])


async def test_get_accounts_with_archive_and_debts_should_return_archived_debts(client: FinstatsClient) -> None:
    actual = await client.get_accounts(show_archive=True, show_debts=True)
    actual_sorted = sorted(actual, key=lambda x: x.id)
    expected = [testdata.ArchivedCashAccount, testdata.ArchivedDebtAccount]
    for i, actual_account in enumerate(actual_sorted):
        _assert_account_matches(expected[i], actual_account)


def _assert_account_matches(expected: Account, actual: AccountModel) -> None:
    assert expected.id == actual.id
    assert expected.changed == actual.changed
    assert expected.user == actual.user
    assert expected.instrument == actual.instrument
    assert expected.title == actual.title
    assert expected.role == actual.role
    assert expected.company == actual.company
    assert expected.type == actual.type
    assert expected.sync_id == actual.sync_id
    assert expected.balance == actual.balance
    assert expected.start_balance == actual.start_balance
    assert expected.credit_limit == actual.credit_limit
    assert expected.in_balance == actual.in_balance
    assert expected.savings == actual.savings
    assert expected.enable_correction == actual.enable_correction
    assert expected.enable_sms == actual.enable_sms
    assert expected.archive == actual.archive
    assert expected.private == actual.private
    assert expected.capitalization == actual.capitalization
    assert expected.percent == actual.percent
    assert expected.start_date == actual.start_date
    assert expected.end_date_offset == actual.end_date_offset
    assert expected.end_date_offset_interval == actual.end_date_offset_interval
    assert expected.payoff_step == actual.payoff_step
    assert expected.payoff_interval == actual.payoff_interval
    assert expected.balance_correction_type == actual.balance_correction_type
