import datetime

import pytest

from finstats.container import Container
from finstats.store import TransactionsRepository, TransactionTypeFilter
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def transactions_repository(container: Container) -> TransactionsRepository:
    return container.resolve(TransactionsRepository)


async def test_empty_db_get_one_should_return_none(transactions_repository: TransactionsRepository) -> None:
    assert await transactions_repository.get_transaction(testdata.TransactionSalary.id) is None


async def test_empty_db_get_many_should_return_empty_array(transactions_repository: TransactionsRepository) -> None:
    actual, total = await transactions_repository.find_transactions()
    assert actual == []
    assert total == 0


async def test_write_read_should_return_transaction(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual = await transactions_repository.get_transaction(testdata.TransactionSalary.id)
    assert actual == testdata.TransactionSalary


async def test_write_read_many_should_return_transactions(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions()
    expected = sorted(testdata.TestTransactions, key=lambda x: x.date, reverse=True)
    assert actual == expected
    assert total == len(testdata.TestTransactions)


async def test_find_transactions_with_offset_limit_should_paginate(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(limit=3, offset=2)
    expected = sorted(testdata.TestTransactions, key=lambda x: x.date, reverse=True)[2:5]
    assert actual == expected
    assert total == len(testdata.TestTransactions)


async def test_find_transactions_with_date_range_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(
        from_date=datetime.date(2026, 1, 18),
        to_date=datetime.date(2026, 1, 21),
    )
    expected = [
        testdata.TransactionRefundIncome,
        testdata.TransactionGroceriesExpense,
        testdata.TransactionTransferCardToWallet,
        testdata.TransactionCafeExpense,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_invalid_date_range_should_raise(transactions_repository: TransactionsRepository) -> None:
    with pytest.raises(ValueError, match="from_date .* > to_date"):
        await transactions_repository.find_transactions(
            from_date=datetime.date(2026, 1, 20),
            to_date=datetime.date(2026, 1, 18),
        )


async def test_find_transactions_with_not_viewed_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(not_viewed=True)
    expected = [
        testdata.TransactionBusExpense,
        testdata.TransactionRefundIncome,
        testdata.TransactionTransferCardToWallet,
        testdata.TransactionSalary,
        testdata.TransactionElectronicsExpense,
        testdata.TransactionExchangeTransfer,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_account_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(account_id=testdata.CashAccount.id)
    expected = [
        testdata.TransactionCafeExpense,
        testdata.TransactionSalary,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_tags_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(tags=[testdata.TagTravel.id])
    expected = [
        testdata.TransactionCashbackIncome,
        testdata.TransactionRefundIncome,
        testdata.TransactionExchangeTransfer,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_income_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionTypeFilter.Income)
    expected = [
        testdata.TransactionCashbackIncome,
        testdata.TransactionRefundIncome,
        testdata.TransactionSalary,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_expense_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionTypeFilter.Expense)
    expected = [
        testdata.TransactionBusExpense,
        testdata.TransactionGroceriesExpense,
        testdata.TransactionCafeExpense,
        testdata.TransactionElectronicsExpense,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_transfer_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionTypeFilter.Transfer)
    expected = [
        testdata.TransactionTransferCashToWallet,
        testdata.TransactionTransferCardToWallet,
        testdata.TransactionExchangeTransfer,
    ]
    assert actual == expected
    assert total == len(expected)
