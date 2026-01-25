import datetime

import pytest

from finstats.container import Container
from finstats.server.models import TransactionType
from finstats.store import AccountsRepository, TagsRepository, TransactionsRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def transactions_repository(container: Container) -> TransactionsRepository:
    return container.resolve(TransactionsRepository)


@pytest.fixture(scope="session")
def accounts_repository(container: Container) -> AccountsRepository:
    return container.resolve(AccountsRepository)


@pytest.fixture(scope="session")
def tags_repository(container: Container) -> TagsRepository:
    return container.resolve(TagsRepository)


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
        testdata.TransactionLentOut,
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
        testdata.TransactionTransportExpense,
        testdata.TransactionRefundIncome,
        testdata.TransactionLentOut,
        testdata.TransactionSalaryReturn,
        testdata.TransactionSalary,
        testdata.TransactionNoTagExpense,
        testdata.TransactionExchangeTransfer,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_account_should_filter(transactions_repository: TransactionsRepository) -> None:
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(account_id=testdata.CashAccount.id)
    expected = [
        testdata.TransactionCafeExpense,
        testdata.TransactionSalaryReturn,
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


async def test_find_transactions_with_type_income_should_filter(
    transactions_repository: TransactionsRepository,
    accounts_repository: AccountsRepository,
    tags_repository: TagsRepository,
) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await tags_repository.save_tags(testdata.TestTags)
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionType.Income)
    expected = [
        testdata.TransactionSalary,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_expense_should_filter(
    transactions_repository: TransactionsRepository,
    accounts_repository: AccountsRepository,
    tags_repository: TagsRepository,
) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await tags_repository.save_tags(testdata.TestTags)
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionType.Expense)
    expected = [
        testdata.TransactionTransportExpense,  # Transport tag is of type 'Both'
        testdata.TransactionGroceriesExpense,  # Groceries tag is of type 'None'
        testdata.TransactionCafeExpense,
        testdata.TransactionNoTagExpense,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_transfer_should_filter(
    transactions_repository: TransactionsRepository,
    accounts_repository: AccountsRepository,
    tags_repository: TagsRepository,
) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await tags_repository.save_tags(testdata.TestTags)
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionType.Transfer)
    expected = [
        testdata.TransactionTransferCashToWallet,
        testdata.TransactionExchangeTransfer,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_lent_out_should_filter(
    transactions_repository: TransactionsRepository,
    accounts_repository: AccountsRepository,
    tags_repository: TagsRepository,
) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await tags_repository.save_tags(testdata.TestTags)
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionType.LentOut)
    expected = [
        testdata.TransactionLentOut,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_debt_repaid_should_filter(
    transactions_repository: TransactionsRepository,
    accounts_repository: AccountsRepository,
    tags_repository: TagsRepository,
) -> None:
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await tags_repository.save_tags(testdata.TestTags)
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionType.DebtRepaid)
    expected = [
        testdata.TransactionDebtRepaid,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_income_return_should_filter(
    transactions_repository: TransactionsRepository,
    accounts_repository: AccountsRepository,
    tags_repository: TagsRepository,
) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionType.ReturnIncome)
    expected = [
        # Travel tag is of type 'Outcome'
        testdata.TransactionCashbackIncome,
        testdata.TransactionRefundIncome,
    ]
    assert actual == expected
    assert total == len(expected)


async def test_find_transactions_with_type_expense_return_should_filter(
    transactions_repository: TransactionsRepository,
    accounts_repository: AccountsRepository,
    tags_repository: TagsRepository,
) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    await accounts_repository.save_accounts(testdata.TestAccounts)
    await transactions_repository.save_transactions(testdata.TestTransactions)
    actual, total = await transactions_repository.find_transactions(transaction_type=TransactionType.ReturnExpense)
    expected = [
        # Salary tag is of type 'Income'
        testdata.TransactionSalaryReturn,
    ]
    assert actual == expected
    assert total == len(expected)
