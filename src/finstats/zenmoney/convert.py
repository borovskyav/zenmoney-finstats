from __future__ import annotations

import dataclasses
import decimal
import time as time_module
import uuid

from finstats.domain import (
    Account,
    Company,
    Country,
    Instrument,
    Merchant,
    Tag,
    Transaction,
    User,
    ZenmoneyDiff,
)
from finstats.zenmoney.models import (
    ZmAccount,
    ZmCompany,
    ZmCountry,
    ZmDiffRequest,
    ZmDiffResponse,
    ZmInstrument,
    ZmMerchant,
    ZmTag,
    ZmTransaction,
    ZmUser,
)


def zm_diff_to_diff(diff: ZmDiffResponse) -> ZenmoneyDiff:
    return ZenmoneyDiff(
        server_timestamp=diff.server_timestamp,
        accounts=zm_accounts_to_accounts(diff.account),
        companies=zm_companies_to_companies(diff.company),
        countries=zm_countries_to_countries(diff.country),
        instruments=zm_instruments_to_instruments(diff.instrument),
        merchants=zm_merchants_to_merchants(diff.merchant),
        tags=zm_tags_to_tags(diff.tag),
        transactions=zm_transactions_to_transactions(diff.transaction),
        users=zm_users_to_users(diff.user),
    )


def diff_to_zm_diff(diff: ZenmoneyDiff) -> ZmDiffRequest:
    return ZmDiffRequest(
        server_timestamp=diff.server_timestamp,
        client_timestamp=int(time_module.time()),
        transaction=None if not diff.transactions else transactions_to_zm_transactions(diff.transactions),
    )


# Account conversions
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


# Transaction conversions
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


# User conversions
def zm_user_to_user(user: ZmUser) -> User:
    return User(**dataclasses.asdict(user))


def zm_users_to_users(users: list[ZmUser]) -> list[User]:
    return [zm_user_to_user(user) for user in users]


def user_to_zm_user(user: User) -> ZmUser:
    return ZmUser(**dataclasses.asdict(user))


def users_to_zm_users(users: list[User]) -> list[ZmUser]:
    return [user_to_zm_user(user) for user in users]


# Tag conversions
def zm_tag_to_tag(tag: ZmTag) -> Tag:
    return Tag(**dataclasses.asdict(tag))


def zm_tags_to_tags(tags: list[ZmTag]) -> list[Tag]:
    return [zm_tag_to_tag(tag) for tag in tags]


def tag_to_zm_tag(tag: Tag) -> ZmTag:
    return ZmTag(**dataclasses.asdict(tag))


def tags_to_zm_tags(tags: list[Tag]) -> list[ZmTag]:
    return [tag_to_zm_tag(tag) for tag in tags]


# Instrument conversions
def zm_instrument_to_instrument(instrument: ZmInstrument) -> Instrument:
    return Instrument(**dataclasses.asdict(instrument))


def zm_instruments_to_instruments(instruments: list[ZmInstrument]) -> list[Instrument]:
    return [zm_instrument_to_instrument(instrument) for instrument in instruments]


def instrument_to_zm_instrument(instrument: Instrument) -> ZmInstrument:
    return ZmInstrument(**dataclasses.asdict(instrument))


def instruments_to_zm_instruments(instruments: list[Instrument]) -> list[ZmInstrument]:
    return [instrument_to_zm_instrument(instrument) for instrument in instruments]


# Country conversions
def zm_country_to_country(country: ZmCountry) -> Country:
    return Country(**dataclasses.asdict(country))


def zm_countries_to_countries(countries: list[ZmCountry]) -> list[Country]:
    return [zm_country_to_country(country) for country in countries]


def country_to_zm_country(country: Country) -> ZmCountry:
    return ZmCountry(**dataclasses.asdict(country))


def countries_to_zm_countries(countries: list[Country]) -> list[ZmCountry]:
    return [country_to_zm_country(country) for country in countries]


# Merchant conversions
def zm_merchant_to_merchant(merchant: ZmMerchant) -> Merchant:
    return Merchant(**dataclasses.asdict(merchant))


def zm_merchants_to_merchants(merchants: list[ZmMerchant]) -> list[Merchant]:
    return [zm_merchant_to_merchant(merchant) for merchant in merchants]


def merchant_to_zm_merchant(merchant: Merchant) -> ZmMerchant:
    return ZmMerchant(**dataclasses.asdict(merchant))


def merchants_to_zm_merchants(merchants: list[Merchant]) -> list[ZmMerchant]:
    return [merchant_to_zm_merchant(merchant) for merchant in merchants]


# Company conversions
def zm_company_to_company(company: ZmCompany) -> Company:
    return Company(**dataclasses.asdict(company))


def zm_companies_to_companies(companies: list[ZmCompany]) -> list[Company]:
    return [zm_company_to_company(company) for company in companies]


def company_to_zm_company(company: Company) -> ZmCompany:
    return ZmCompany(**dataclasses.asdict(company))


def companies_to_zm_companies(companies: list[Company]) -> list[ZmCompany]:
    return [company_to_zm_company(company) for company in companies]


# Helper functions
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
