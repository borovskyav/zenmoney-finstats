from __future__ import annotations

import dataclasses
import datetime
import decimal
from typing import Annotated

import marshmallow_recipe as mr

from finstats.domain import (
    AccountId,
    CompanyId,
    CountryId,
    InstrumentId,
    MerchantId,
    ReminderMarkerId,
    Tag,
    TagId,
    TagType,
    Transaction,
    TransactionId,
    TransactionType,
    UserId,
)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class AccountModel:
    id: Annotated[AccountId, mr.meta(description="Unique identifier of the account")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this account")]
    instrument: Annotated[InstrumentId, mr.meta(description="Currency/instrument ID for the account")]
    title: Annotated[str, mr.meta(description="Account title")]
    role: Annotated[int | None, mr.meta(description="Account role identifier from the source system")] = None
    company: Annotated[CompanyId | None, mr.meta(description="Company ID associated with the account")] = None
    type: Annotated[str, mr.meta(description="Account type")]
    sync_id: Annotated[list[str] | None, mr.meta(name="syncID", description="External sync identifiers for the account")]
    balance: Annotated[decimal.Decimal, mr.meta(description="Current account balance")]
    start_balance: Annotated[decimal.Decimal, mr.meta(description="Starting balance (initial deposit or loan principal)")]
    credit_limit: Annotated[decimal.Decimal, mr.meta(description="Credit limit for the account")]
    in_balance: Annotated[bool, mr.meta(description="Whether the account is included in overall balance")]
    savings: Annotated[bool, mr.meta(description="Whether the account is marked as savings")]
    enable_correction: Annotated[bool, mr.meta(description="Whether balance correction is enabled")]
    enable_sms: Annotated[bool, mr.meta(name="enableSMS", description="Whether SMS notifications are enabled")]
    archive: Annotated[bool, mr.meta(description="Whether the account is archived")]
    private: Annotated[bool, mr.meta(description="Whether the account is private")]
    capitalization: Annotated[str | None, mr.meta(description="Capitalization type for deposit/loan accounts")] = None
    percent: Annotated[decimal.Decimal | None, mr.meta(description="Interest rate for deposit/loan accounts")] = None
    start_date: Annotated[
        datetime.datetime | None,
        mr.datetime_meta(format="timestamp"),
        mr.meta(description="Start date for deposit/loan accounts"),
    ] = None
    end_date_offset: Annotated[int | None, mr.meta(description="End date offset value for deposit/loan accounts")] = None
    end_date_offset_interval: Annotated[str | None, mr.meta(description="End date offset interval unit")] = None
    payoff_step: Annotated[int | None, mr.meta(description="Payoff step value for loan accounts")] = None
    payoff_interval: Annotated[str | None, mr.meta(description="Payoff interval unit for loan accounts")] = None
    balance_correction_type: Annotated[str, mr.meta(description="Balance correction type")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class TransactionModel:
    id: Annotated[TransactionId, mr.meta(description="Unique identifier of the transaction")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    created: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Transaction creation timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this transaction")]
    deleted: Annotated[bool, mr.meta(description="Whether the transaction has been deleted")]
    hold: Annotated[bool | None, mr.meta(description="Whether the transaction is on hold (pending)")] = None
    viewed: Annotated[bool, mr.meta(description="Whether the transaction has been viewed by the user")]
    qr_code: Annotated[str | None, mr.meta(description="QR code associated with the transaction")] = None
    income_bank: Annotated[str | None, mr.meta(name="incomeBankID", description="Bank ID for the income side of the transaction")] = None
    income_instrument: Annotated[InstrumentId, mr.meta(description="Currency/instrument ID for the income")]
    income_account: Annotated[AccountId, mr.meta(description="Account ID receiving the income")]
    income: Annotated[decimal.Decimal, mr.meta(description="Income amount in the income account's currency")]
    outcome_bank: Annotated[str | None, mr.meta(name="outcomeBankID", description="Bank ID for the outcome side of the transaction")] = None
    outcome_instrument: Annotated[InstrumentId, mr.meta(description="Currency/instrument ID for the outcome")]
    outcome_account: Annotated[AccountId, mr.meta(description="Account ID from which the outcome is withdrawn")]
    outcome: Annotated[decimal.Decimal, mr.meta(description="Outcome amount in the outcome account's currency")]
    merchant: Annotated[MerchantId | None, mr.meta(description="ID of the merchant associated with the transaction")] = None
    payee: Annotated[str | None, mr.meta(description="Name of the payee/recipient")] = None
    original_payee: Annotated[str | None, mr.meta(description="Original payee name before user modifications")] = None
    comment: Annotated[str | None, mr.meta(description="User's comment or note about the transaction")] = None
    date: Annotated[datetime.date, mr.meta(description="Transaction date")] = dataclasses.field(metadata=mr.datetime_meta(format="%Y-%m-%d"))
    mcc: Annotated[int | None, mr.meta(description="Merchant Category Code (MCC) for the transaction")] = None
    reminder_marker: Annotated[ReminderMarkerId | None, mr.meta(description="ID of the associated reminder marker")] = None
    op_income: Annotated[decimal.Decimal | None, mr.meta(description="Original income amount before currency conversion")] = None
    op_income_instrument: Annotated[InstrumentId | None, mr.meta(description="Original income currency/instrument ID")] = None
    op_outcome: Annotated[decimal.Decimal | None, mr.meta(description="Original outcome amount before currency conversion")] = None
    op_outcome_instrument: Annotated[InstrumentId | None, mr.meta(description="Original outcome currency/instrument ID")] = None
    latitude: Annotated[float | None, mr.meta(description="Geographical latitude where the transaction occurred")] = None
    longitude: Annotated[float | None, mr.meta(description="Geographical longitude where the transaction occurred")] = None
    source: Annotated[str | None, mr.meta(description="Source of the transaction (manual, import, sync, etc.)")] = None
    tags: Annotated[list[TagId], mr.list_meta(description="List of tag IDs associated with the transaction")]

    tags_titles: Annotated[list[str], mr.meta(description="Human-readable titles for the tags field, in the same order as IDs in tags")]
    income_instrument_title: Annotated[str, mr.meta(description="Human-readable title for the incomeInstrument field")]
    outcome_instrument_title: Annotated[str, mr.meta(description="Human-readable title for the outcomeInstrument field")]
    income_account_title: Annotated[str, mr.meta(description="Human-readable title for the incomeAccount field")]
    outcome_account_title: Annotated[str, mr.meta(description="Human-readable title for the outcomeAccount field")]
    merchant_title: Annotated[str | None, mr.meta(description="Human-readable title for the merchant field")]
    transaction_type: Annotated[TransactionType, mr.meta(description="Computed transaction type: Income, Expense, Transfer, DebtRepaid, or LentOut")]


def _calculate_transaction_type(
    transaction: Transaction,
    income_account_type: str | None,
    outcome_account_type: str | None,
    tag: Tag | None,
) -> TransactionType:
    if transaction.outcome == 0 and transaction.income > 0:
        tag_type = _calculate_tag_type(tag) if tag else None
        return TransactionType.ReturnIncome if tag_type == TagType.Expense else TransactionType.Income
    if transaction.income == 0 and transaction.outcome > 0:
        tag_type = _calculate_tag_type(tag) if tag else None
        return TransactionType.ReturnExpense if tag_type == TagType.Income else TransactionType.Expense
    if transaction.income > 0 and transaction.outcome > 0:
        if income_account_type == "debt":
            return TransactionType.LentOut
        if outcome_account_type == "debt":
            return TransactionType.DebtRepaid
        return TransactionType.Transfer
    return TransactionType.Transfer


def _calculate_tag_type(tag: Tag) -> str | None:
    if tag.show_income and tag.show_outcome:
        return TagType.Both
    if tag.show_income:
        return TagType.Income
    if tag.show_outcome:
        return TagType.Expense
    return None


def _use_tag_in_analytics(tag: Tag) -> bool:
    return (tag.show_income and tag.budget_income) or (tag.show_outcome and tag.budget_outcome)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class UserModel:
    id: Annotated[UserId, mr.meta(description="Unique identifier of the user")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    currency: Annotated[InstrumentId, mr.meta(description="Default currency/instrument ID for the user")]
    parent: Annotated[UserId | None, mr.meta(description="Parent user ID, if any")]
    country: Annotated[CountryId | None, mr.meta(description="Country ID of the user")]
    country_code: Annotated[str, mr.meta(description="Country code (ISO 3166-1 alpha-2)")]
    email: Annotated[str | None, mr.meta(description="User's email address")]
    login: Annotated[str | None, mr.meta(description="User's login name")]
    month_start_day: Annotated[int, mr.meta(description="Day of month when financial month starts")]
    is_forecast_enabled: Annotated[bool, mr.meta(description="Whether forecasting is enabled for the user")]
    plan_balance_mode: Annotated[str, mr.meta(description="Plan balance calculation mode")]
    plan_settings: Annotated[str, mr.meta(description="JSON-encoded plan settings")]
    paid_till: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Subscription paid until timestamp")]
    subscription: Annotated[str | None, mr.meta(description="Subscription type")]
    subscription_renewal_date: Annotated[str | None, mr.meta(description="Subscription renewal date")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class TagModel:
    id: Annotated[TagId, mr.meta(description="Unique identifier of the tag")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this tag")]
    title: Annotated[str, mr.meta(description="Tag title")]
    parent: Annotated[TagId | None, mr.meta(description="Parent tag ID, if any")]
    icon: Annotated[str | None, mr.meta(description="Icon identifier for the tag")]
    static_id: Annotated[str | None, mr.meta(description="Static tag identifier from the source system")]
    picture: Annotated[str | None, mr.meta(description="Picture identifier or URL for the tag")]
    color: Annotated[int | None, mr.meta(description="Tag color as an integer value")]
    show_income: Annotated[bool, mr.meta(description="Whether the tag is shown for income transactions")]
    show_outcome: Annotated[bool, mr.meta(description="Whether the tag is shown for outcome transactions")]
    budget_income: Annotated[bool, mr.meta(description="Whether the tag is included in income budgets")]
    budget_outcome: Annotated[bool, mr.meta(description="Whether the tag is included in outcome budgets")]
    required: Annotated[bool | None, mr.meta(description="Whether the tag is required to classify transactions")]
    archive: Annotated[bool, mr.meta(description="Whether the tag is archived")]
    children: Annotated[list[TagId], mr.meta(description="List of children tag IDs")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class InstrumentModel:
    id: Annotated[InstrumentId, mr.meta(description="Unique identifier of the instrument")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    title: Annotated[str, mr.meta(description="Instrument title")]
    short_title: Annotated[str, mr.meta(description="Short instrument title")]
    symbol: Annotated[str, mr.meta(description="Instrument symbol")]
    rate: Annotated[decimal.Decimal, mr.meta(description="Exchange rate relative to the base instrument")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CountryModel:
    id: Annotated[CountryId, mr.meta(description="Unique identifier of the country")]
    title: Annotated[str, mr.meta(description="Country name")]
    currency: Annotated[InstrumentId, mr.meta(description="Default currency/instrument ID for the country")]
    domain: Annotated[str | None, mr.meta(description="Country domain")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class MerchantModel:
    id: Annotated[MerchantId, mr.meta(description="Unique identifier of the merchant")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this merchant")]
    title: Annotated[str, mr.meta(description="Name of the merchant")]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CompanyModel:
    id: Annotated[CompanyId, mr.meta(description="Unique identifier of the company")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    title: Annotated[str, mr.meta(description="Company name")]
    full_title: Annotated[str | None, mr.meta(description="Full company name")]
    www: Annotated[str | None, mr.meta(description="Company website URL")]
    country: Annotated[CountryId | None, mr.meta(description="Country ID of the company")]
    country_code: Annotated[str | None, mr.meta(description="Country code (ISO 3166-1 alpha-2)")]
    deleted: Annotated[bool, mr.meta(description="Whether the company is deleted")]
