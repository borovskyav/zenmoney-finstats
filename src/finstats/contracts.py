from __future__ import annotations

import abc
import dataclasses
import datetime
import decimal
import uuid
from typing import Annotated

import marshmallow_recipe as mr


class CliException(Exception):
    pass


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


InstrumentId = int
UserId = int
CountryId = int
TagId = uuid.UUID
CompanyId = int
AccountId = uuid.UUID
MerchantId = uuid.UUID
TransactionId = uuid.UUID
ReminderMarkerId = uuid.UUID


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmUser:
    id: UserId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    currency: InstrumentId
    parent: UserId | None
    country: CountryId
    country_code: str
    email: str | None
    login: str | None
    month_start_day: int
    is_forecast_enabled: bool
    plan_balance_mode: str
    plan_settings: str
    paid_till: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    subscription: str  # '10yearssubscription' | '1MonthSubscription'
    subscription_renewal_date: str | None


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
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


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmInstrument:
    id: InstrumentId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    title: str
    short_title: str
    symbol: str
    rate: decimal.Decimal


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmCountry:
    id: CountryId
    title: str
    currency: InstrumentId
    domain: str | None


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmCompany:
    id: CompanyId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    title: str
    full_title: str | None
    www: str | None
    country: CountryId | None
    country_code: str | None  # RU
    deleted: bool


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmAccount:
    id: AccountId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    instrument: InstrumentId
    title: str
    role: int | None
    company: CompanyId | None
    type: str
    sync_id: Annotated[list[str] | None, mr.meta(name="syncID")]
    balance: decimal.Decimal
    start_balance: decimal.Decimal  # Для deposit и loan поле startBalance имеет смысл начального взноса/тела кредита
    credit_limit: decimal.Decimal
    in_balance: bool
    savings: bool
    enable_correction: bool
    enable_sms: Annotated[bool, mr.meta(name="enableSMS")]
    archive: bool
    private: bool
    # Для счетов с типом отличных от 'loan' и 'deposit' в  этих полях можно ставить null
    capitalization: str | None
    percent: decimal.Decimal | None
    start_date: Annotated[datetime.datetime | None, mr.datetime_meta(format="timestamp")]
    end_date_offset: int | None
    end_date_offset_interval: str | None  # 'day' | 'week' | 'month' | 'year' | null
    payoff_step: int | None
    payoff_interval: str | None  # 'month' | 'year' | null
    balance_correction_type: str


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmMerchant:
    id: MerchantId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    title: str


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmTransaction:
    id: TransactionId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    created: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    deleted: bool
    hold: bool | None
    viewed: bool
    qr_code: str | None
    income_bank: Annotated[str | None, mr.meta(name="incomeBankID")]
    income_instrument: InstrumentId
    income_account: AccountId
    income: decimal.Decimal
    outcome_bank: Annotated[str | None, mr.meta(name="outcomeBankID")]
    outcome_instrument: InstrumentId
    outcome_account: AccountId
    outcome: decimal.Decimal
    tag: list[TagId] | None
    merchant: MerchantId | None
    payee: str | None
    original_payee: str | None
    comment: str | None
    date: datetime.date = dataclasses.field(metadata=mr.datetime_meta(format="%Y-%m-%d"))
    mcc: int | None
    reminder_marker: ReminderMarkerId | None
    op_income: decimal.Decimal | None
    op_income_instrument: InstrumentId | None
    op_outcome: decimal.Decimal | None
    op_outcome_instrument: InstrumentId | None
    latitude: decimal.Decimal | None
    longitude: decimal.Decimal | None
    source: str | None


class DiffClient(abc.ABC):
    @abc.abstractmethod
    async def fetch_diff(self, server_timestamp: int) -> ZmDiffResponse: ...
