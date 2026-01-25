from __future__ import annotations

import dataclasses
from typing import Any

from client import (
    AccountModel,
    CompanyModel,
    CountryModel,
    InstrumentModel,
    MerchantModel,
    TagModel,
    TagType,
    TransactionModel,
    TransactionType,
    UserModel,
)
from finstats.domain import (
    Account,
    Company,
    Country,
    Instrument,
    Merchant,
    Tag,
    TagId,
    Transaction,
    User,
)


# Account conversions
def account_model_to_account(account: AccountModel) -> Account:
    data = _filter_fields(dataclasses.asdict(account), Account)
    return Account(**data)


def account_models_to_accounts(accounts: list[AccountModel]) -> list[Account]:
    return [account_model_to_account(account) for account in accounts]


def account_to_account_model(account: Account) -> AccountModel:
    data = _filter_fields(dataclasses.asdict(account), AccountModel)
    return AccountModel(**data)


def accounts_to_account_models(accounts: list[Account]) -> list[AccountModel]:
    return [account_to_account_model(account) for account in accounts]


# Transaction conversions
def transaction_model_to_transaction(transaction: TransactionModel) -> Transaction:
    data = _filter_fields(dataclasses.asdict(transaction), Transaction)
    return Transaction(**data)


def transaction_models_to_transactions(transactions: list[TransactionModel]) -> list[Transaction]:
    return [transaction_model_to_transaction(transaction) for transaction in transactions]


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


# User conversions
def user_model_to_user(user: UserModel) -> User:
    return User(**dataclasses.asdict(user))


def user_models_to_users(users: list[UserModel]) -> list[User]:
    return [user_model_to_user(user) for user in users]


def user_to_user_model(user: User) -> UserModel:
    return UserModel(**dataclasses.asdict(user))


def users_to_user_models(users: list[User]) -> list[UserModel]:
    return [user_to_user_model(user) for user in users]


# Tag conversions
def tag_model_to_tag(tag: TagModel) -> Tag:
    data = _filter_fields(dataclasses.asdict(tag), Tag)
    return Tag(**data)


def tag_models_to_tags(tags: list[TagModel]) -> list[Tag]:
    return [tag_model_to_tag(tag) for tag in tags]


def tag_to_tag_model(tag: Tag, *, children_ids: list[TagId]) -> TagModel:
    return TagModel(**dataclasses.asdict(tag), children=children_ids)


def tags_to_tag_models(tags: list[Tag], *, children_ids_map: dict[TagId, list[TagId]]) -> list[TagModel]:
    return [tag_to_tag_model(tag, children_ids=children_ids_map.get(tag.id, [])) for tag in tags]


# Instrument conversions
def instrument_model_to_instrument(instrument: InstrumentModel) -> Instrument:
    return Instrument(**dataclasses.asdict(instrument))


def instrument_models_to_instruments(instruments: list[InstrumentModel]) -> list[Instrument]:
    return [instrument_model_to_instrument(instrument) for instrument in instruments]


def instrument_to_instrument_model(instrument: Instrument) -> InstrumentModel:
    return InstrumentModel(**dataclasses.asdict(instrument))


def instruments_to_instrument_models(instruments: list[Instrument]) -> list[InstrumentModel]:
    return [instrument_to_instrument_model(instrument) for instrument in instruments]


# Country conversions
def country_model_to_country(country: CountryModel) -> Country:
    return Country(**dataclasses.asdict(country))


def country_models_to_countries(countries: list[CountryModel]) -> list[Country]:
    return [country_model_to_country(country) for country in countries]


def country_to_country_model(country: Country) -> CountryModel:
    return CountryModel(**dataclasses.asdict(country))


def countries_to_country_models(countries: list[Country]) -> list[CountryModel]:
    return [country_to_country_model(country) for country in countries]


# Merchant conversions
def merchant_model_to_merchant(merchant: MerchantModel) -> Merchant:
    return Merchant(**dataclasses.asdict(merchant))


def merchant_models_to_merchants(merchants: list[MerchantModel]) -> list[Merchant]:
    return [merchant_model_to_merchant(merchant) for merchant in merchants]


def merchant_to_merchant_model(merchant: Merchant) -> MerchantModel:
    return MerchantModel(**dataclasses.asdict(merchant))


def merchants_to_merchant_models(merchants: list[Merchant]) -> list[MerchantModel]:
    return [merchant_to_merchant_model(merchant) for merchant in merchants]


# Company conversions
def company_model_to_company(company: CompanyModel) -> Company:
    return Company(**dataclasses.asdict(company))


def company_models_to_companies(companies: list[CompanyModel]) -> list[Company]:
    return [company_model_to_company(company) for company in companies]


def company_to_company_model(company: Company) -> CompanyModel:
    return CompanyModel(**dataclasses.asdict(company))


def companies_to_company_models(companies: list[Company]) -> list[CompanyModel]:
    return [company_to_company_model(company) for company in companies]


def _filter_fields(data: dict[str, Any], target_type: type) -> dict[str, Any]:
    allowed = {field.name for field in dataclasses.fields(target_type)}
    return {key: value for key, value in data.items() if key in allowed}


def calculate_transaction_type(
    transaction: Transaction,
    income_account_type: str | None,
    outcome_account_type: str | None,
    tag: Tag | None,
) -> TransactionType:
    if transaction.outcome == 0 and transaction.income > 0:
        tag_type = calculate_tag_type(tag) if tag else None
        return TransactionType.ReturnIncome if tag_type == TagType.Expense else TransactionType.Income
    if transaction.income == 0 and transaction.outcome > 0:
        tag_type = calculate_tag_type(tag) if tag else None
        return TransactionType.ReturnExpense if tag_type == TagType.Income else TransactionType.Expense
    if transaction.income > 0 and transaction.outcome > 0:
        if income_account_type == "debt":
            return TransactionType.LentOut
        if outcome_account_type == "debt":
            return TransactionType.DebtRepaid
        return TransactionType.Transfer
    return TransactionType.Transfer


def calculate_tag_type(tag: Tag) -> TagType | None:
    if tag.show_income and tag.show_outcome:
        return TagType.Both
    if tag.show_income:
        return TagType.Income
    if tag.show_outcome:
        return TagType.Expense
    return None
