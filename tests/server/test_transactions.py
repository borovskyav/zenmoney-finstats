import pytest

from client import TransactionModel
from client.client import FinstatsClient
from finstats.domain import Transaction
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_transactions_with_base_filters_should_return_all_transactions(client: FinstatsClient) -> None:
    response = await client.get_transactions()
    expected = sorted(testdata.TestTransactions, key=lambda x: (x.date, x.created, x.id), reverse=True)
    actual = response.transactions
    assert response.total_count == len(expected)
    assert len(actual) == len(expected)
    for i, actual_transaction in enumerate(actual):
        _assert_transaction_matches(expected[i], actual_transaction)


def _get_base_sorted_transactions() -> list[Transaction]:
    return sorted(
        testdata.TestTransactions,
        key=lambda x: (x.date, x.created, x.id),
        reverse=True,
    )


def _assert_transaction_matches(expected: Transaction, actual: TransactionModel) -> None:
    assert expected.id == actual.id
    assert expected.changed == actual.changed
    assert expected.created == actual.created
    assert expected.user == actual.user
    assert expected.deleted == actual.deleted
    assert expected.hold == actual.hold
    assert expected.viewed == actual.viewed
    assert expected.qr_code == actual.qr_code
    assert expected.income_bank == actual.income_bank
    assert expected.income_instrument == actual.income_instrument
    assert expected.income_account == actual.income_account
    assert expected.income == actual.income
    assert expected.outcome_bank == actual.outcome_bank
    assert expected.outcome_instrument == actual.outcome_instrument
    assert expected.outcome_account == actual.outcome_account
    assert expected.outcome == actual.outcome
    assert expected.merchant == actual.merchant
    assert expected.payee == actual.payee
    assert expected.original_payee == actual.original_payee
    assert expected.comment == actual.comment
    assert expected.date == actual.date
    assert expected.mcc == actual.mcc
    assert expected.reminder_marker == actual.reminder_marker
    assert expected.op_income == actual.op_income
    assert expected.op_income_instrument == actual.op_income_instrument
    assert expected.op_outcome == actual.op_outcome
    assert expected.op_outcome_instrument == actual.op_outcome_instrument
    assert expected.latitude == actual.latitude
    assert expected.longitude == actual.longitude
    assert expected.source == actual.source
    assert expected.tags == actual.tags
