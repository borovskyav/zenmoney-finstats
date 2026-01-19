from __future__ import annotations

import dataclasses
import decimal
import time as time_module
import uuid

from finstats.domain import Account, Transaction, ZenmoneyDiff
from finstats.zenmoney.models import ZmAccount, ZmDiffRequest, ZmDiffResponse, ZmTransaction


def zm_diff_to_diff(diff: ZmDiffResponse) -> ZenmoneyDiff:
    return ZenmoneyDiff(
        server_timestamp=diff.server_timestamp,
        accounts=zm_accounts_to_accounts(diff.account),
        companies=diff.company,
        countries=diff.country,
        instruments=diff.instrument,
        merchants=diff.merchant,
        tags=diff.tag,
        transactions=zm_transactions_to_transactions(diff.transaction),
        users=diff.user,
    )


def diff_to_zm_diff(diff: ZenmoneyDiff) -> ZmDiffRequest:
    return ZmDiffRequest(
        server_timestamp=diff.server_timestamp,
        client_timestamp=int(time_module.time()),
        transaction=None if not diff.transactions else transactions_to_zm_transactions(diff.transactions),
    )


def zm_account_to_account(account: ZmAccount) -> Account:
    data = dataclasses.asdict(account)
    _normalize_account_dict(data)
    return Account(**data)


def zm_accounts_to_accounts(accounts: list[ZmAccount]) -> list[Account]:
    return [zm_account_to_account(account) for account in accounts]


def account_to_zm_account(account: Account) -> ZmAccount:
    data = dataclasses.asdict(account)
    _normalize_account_dict(data)
    return ZmAccount(**data)


def accounts_to_zm_accounts(accounts: list[Account]) -> list[ZmAccount]:
    return [account_to_zm_account(account) for account in accounts]


def zm_transaction_to_transaction(transaction: ZmTransaction) -> Transaction:
    data = dataclasses.asdict(transaction)
    _normalize_transaction_dict(data)
    _normalize_transaction_amounts_to_decimal(data)
    return Transaction(**data)


def zm_transactions_to_transactions(transactions: list[ZmTransaction]) -> list[Transaction]:
    return [zm_transaction_to_transaction(transaction) for transaction in transactions]


def transaction_to_zm_transaction(transaction: Transaction) -> ZmTransaction:
    data = dataclasses.asdict(transaction)
    _normalize_transaction_dict(data)
    _normalize_transaction_amounts_to_float(data)
    return ZmTransaction(**data)


def transactions_to_zm_transactions(transactions: list[Transaction]) -> list[ZmTransaction]:
    return [transaction_to_zm_transaction(transaction) for transaction in transactions]


def _normalize_account_dict(data: dict[str, object]) -> None:
    if data.get("sync_id") is None:
        data["sync_id"] = []


def _normalize_transaction_dict(data: dict[str, object]) -> None:
    if data.get("outcome_account") is None:
        data["outcome_account"] = _DEFAULT_OUTCOME_ACCOUNT_ID
    if data.get("tags") is None:
        data["tags"] = []


def _as_decimal(value: object) -> decimal.Decimal:
    if isinstance(value, decimal.Decimal):
        return value
    return decimal.Decimal(str(value))


def _as_float(value: object) -> float:
    if isinstance(value, float):
        return value
    if isinstance(value, decimal.Decimal):
        return float(value)
    raise ValueError("Cannot convert value to float")


def _normalize_transaction_amounts_to_decimal(data: dict[str, object]) -> None:
    for key in ("income", "outcome", "op_income", "op_outcome"):
        value = data.get(key)
        if value is None:
            continue
        data[key] = _as_decimal(value)


def _normalize_transaction_amounts_to_float(data: dict[str, object]) -> None:
    for key in ("income", "outcome", "op_income", "op_outcome"):
        value = data.get(key)
        if value is None:
            continue
        data[key] = _as_float(value)


_DEFAULT_OUTCOME_ACCOUNT_ID = uuid.UUID("5c6d2ce9-4d67-450c-b40d-28a7dea1e20e")
