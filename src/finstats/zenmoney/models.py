from __future__ import annotations

import dataclasses
import datetime
import decimal
from typing import Annotated

import marshmallow_recipe as mr

from finstats.domain import (
    AccountId,
    CompanyId,
    InstrumentId,
    MerchantId,
    ReminderMarkerId,
    TagId,
    TransactionId,
    UserId,
    ZmCompany,
    ZmCountry,
    ZmInstrument,
    ZmMerchant,
    ZmTag,
    ZmUser,
)


class ZenMoneyClientException(Exception):
    pass


class ZenMoneyClientAuthException(ZenMoneyClientException):
    pass


@dataclasses.dataclass(frozen=True, slots=True)
class ZmDiffRequest:
    server_timestamp: Annotated[int, mr.meta(name="serverTimestamp")]
    client_timestamp: Annotated[int, mr.meta(name="currentClientTimestamp")]
    transaction: list[ZmTransaction] | None = None


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmDiffResponse:
    server_timestamp: int
    account: list[ZmAccount] = dataclasses.field(default_factory=list)
    company: list[ZmCompany] = dataclasses.field(default_factory=list)
    country: list[ZmCountry] = dataclasses.field(default_factory=list)
    instrument: list[ZmInstrument] = dataclasses.field(default_factory=list)
    merchant: list[ZmMerchant] = dataclasses.field(default_factory=list)
    tag: list[ZmTag] = dataclasses.field(default_factory=list)
    transaction: list[ZmTransaction] = dataclasses.field(default_factory=list)
    user: list[ZmUser] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmAccount:
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
    # Для счетов с типом отличных от 'loan' и 'deposit' в  этих полях можно ставить null
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
@mr.options(naming_case=mr.CAMEL_CASE, none_value_handling=mr.NoneValueHandling.INCLUDE)
class ZmTransaction:
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
    income: Annotated[float, mr.meta(description="Income amount in the income account's currency")]
    outcome_bank: Annotated[str | None, mr.meta(name="outcomeBankID", description="Bank ID for the outcome side of the transaction")] = None
    outcome_instrument: Annotated[InstrumentId, mr.meta(description="Currency/instrument ID for the outcome")]
    outcome_account: Annotated[AccountId | None, mr.meta(description="Account ID from which the outcome is withdrawn")]
    outcome: Annotated[float, mr.meta(description="Outcome amount in the outcome account's currency")]
    merchant: Annotated[MerchantId | None, mr.meta(description="ID of the merchant associated with the transaction")] = None
    payee: Annotated[str | None, mr.meta(description="Name of the payee/recipient")] = None
    original_payee: Annotated[str | None, mr.meta(description="Original payee name before user modifications")] = None
    comment: Annotated[str | None, mr.meta(description="User's comment or note about the transaction")] = None
    date: Annotated[datetime.date, mr.meta(description="Transaction date")] = dataclasses.field(metadata=mr.datetime_meta(format="%Y-%m-%d"))
    mcc: Annotated[int | None, mr.meta(description="Merchant Category Code (MCC) for the transaction")] = None
    reminder_marker: Annotated[ReminderMarkerId | None, mr.meta(description="ID of the associated reminder marker")] = None
    op_income: Annotated[float | None, mr.meta(description="Original income amount before currency conversion")] = None
    op_income_instrument: Annotated[InstrumentId | None, mr.meta(description="Original income currency/instrument ID")] = None
    op_outcome: Annotated[float | None, mr.meta(description="Original outcome amount before currency conversion")] = None
    op_outcome_instrument: Annotated[InstrumentId | None, mr.meta(description="Original outcome currency/instrument ID")] = None
    latitude: Annotated[float | None, mr.meta(description="Geographical latitude where the transaction occurred")] = None
    longitude: Annotated[float | None, mr.meta(description="Geographical longitude where the transaction occurred")] = None
    source: Annotated[str | None, mr.meta(description="Source of the transaction (manual, import, sync, etc.)")] = None
    tags: Annotated[list[TagId] | None, mr.meta(description="List of tag IDs associated with the transaction")] = dataclasses.field(
        default_factory=list, metadata=mr.list_meta(name="tag")
    )
