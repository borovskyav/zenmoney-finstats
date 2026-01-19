from __future__ import annotations

import dataclasses
from typing import Any

from finstats.domain import Account, Transaction
from finstats.http.models import AccountModel, TransactionModel, TransactionType


def account_model_to_account(account: AccountModel) -> Account:
    data = _filter_fields(dataclasses.asdict(account), Account)
    return Account(**data)


def account_models_to_accounts(accounts: list[AccountModel]) -> list[Account]:
    return [account_model_to_account(account) for account in accounts]


def transaction_model_to_transaction(transaction: TransactionModel) -> Transaction:
    data = _filter_fields(dataclasses.asdict(transaction), Transaction)
    return Transaction(**data)


def transaction_models_to_transactions(transactions: list[TransactionModel]) -> list[Transaction]:
    return [transaction_model_to_transaction(transaction) for transaction in transactions]


def account_to_account_model(account: Account) -> AccountModel:
    data = _filter_fields(dataclasses.asdict(account), AccountModel)
    return AccountModel(**data)


def accounts_to_account_models(accounts: list[Account]) -> list[AccountModel]:
    return [account_to_account_model(account) for account in accounts]


def transaction_to_transaction_model(
    transaction: Transaction,
    *,
    tags_titles: list[str],
    income_instrument_title: str,
    outcome_instrument_title: str,
    income_account_title: str,
    outcome_account_title: str,
    merchant_title: str | None,
    transaction_type: TransactionType,
) -> TransactionModel:
    data = _filter_fields(dataclasses.asdict(transaction), TransactionModel)
    data.update(
        {
            "tags_titles": tags_titles,
            "income_instrument_title": income_instrument_title,
            "outcome_instrument_title": outcome_instrument_title,
            "income_account_title": income_account_title,
            "outcome_account_title": outcome_account_title,
            "merchant_title": merchant_title,
            "transaction_type": transaction_type,
        }
    )
    return TransactionModel(**data)


def _filter_fields(data: dict[str, Any], target_type: type) -> dict[str, Any]:
    allowed = {field.name for field in dataclasses.fields(target_type)}
    return {key: value for key, value in data.items() if key in allowed}
