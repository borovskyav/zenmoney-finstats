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
    TagId,
    TransactionId,
    UserId,
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
class ZmAccount:
    id: AccountId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    instrument: InstrumentId
    title: str
    role: int | None = None
    company: CompanyId | None = None
    type: str
    sync_id: Annotated[list[str] | None, mr.meta(name="syncID")]
    balance: decimal.Decimal
    start_balance: decimal.Decimal
    credit_limit: decimal.Decimal
    in_balance: bool
    savings: bool
    enable_correction: bool
    enable_sms: Annotated[bool, mr.meta(name="enableSMS")]
    archive: bool
    private: bool
    capitalization: str | None = None
    percent: decimal.Decimal | None = None
    start_date: Annotated[datetime.datetime | None, mr.datetime_meta(format="timestamp")] = None
    end_date_offset: int | None = None
    end_date_offset_interval: str | None = None
    payoff_step: int | None = None
    payoff_interval: str | None = None
    balance_correction_type: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
@mr.options(naming_case=mr.CAMEL_CASE, none_value_handling=mr.NoneValueHandling.INCLUDE)
class ZmTransaction:
    id: TransactionId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    created: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    deleted: bool
    hold: bool | None = None
    viewed: bool
    qr_code: str | None = None
    income_bank: Annotated[str | None, mr.meta(name="incomeBankID")] = None
    income_instrument: InstrumentId
    income_account: AccountId
    income: Annotated[decimal.Decimal, mr.decimal_meta(as_string=False)]
    outcome_bank: Annotated[str | None, mr.meta(name="outcomeBankID")] = None
    outcome_instrument: InstrumentId
    outcome_account: AccountId | None
    outcome: Annotated[decimal.Decimal, mr.decimal_meta(as_string=False)]
    merchant: MerchantId | None = None
    payee: str | None = None
    original_payee: str | None = None
    comment: str | None = None
    date: Annotated[datetime.date, mr.datetime_meta(format="%Y-%m-%d")]
    mcc: int | None = None
    reminder_marker: ReminderMarkerId | None = None
    op_income: Annotated[decimal.Decimal | None, mr.decimal_meta(as_string=False)] = None
    op_income_instrument: InstrumentId | None = None
    op_outcome: Annotated[decimal.Decimal | None, mr.decimal_meta(as_string=False)] = None
    op_outcome_instrument: InstrumentId | None = None
    latitude: float | None = None
    longitude: float | None = None
    source: str | None = None
    tags: Annotated[list[TagId] | None, mr.list_meta(name="tag")] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZmUser:
    id: UserId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    currency: InstrumentId
    parent: UserId | None
    country: CountryId | None
    country_code: str
    email: str | None
    login: str | None
    month_start_day: int
    is_forecast_enabled: bool
    plan_balance_mode: str
    plan_settings: str
    paid_till: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    subscription: str | None  # '10yearssubscription' | '1MonthSubscription' | None
    subscription_renewal_date: str | None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZmTag:
    id: TagId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    title: str
    parent: TagId | None
    icon: str | None
    static_id: str | None
    picture: str | None
    color: int | None
    show_income: bool
    show_outcome: bool
    budget_income: bool
    budget_outcome: bool
    required: bool | None
    archive: bool


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZmInstrument:
    id: InstrumentId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    title: str
    short_title: str
    symbol: str
    rate: decimal.Decimal


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZmCountry:
    id: CountryId
    title: str
    currency: InstrumentId
    domain: str | None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZmMerchant:
    id: MerchantId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    title: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZmCompany:
    id: CompanyId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    title: str
    full_title: str | None
    www: str | None
    country: CountryId | None
    country_code: str | None  # RU
    deleted: bool
