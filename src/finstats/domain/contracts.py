from __future__ import annotations

import dataclasses
import datetime
import decimal
import uuid
from typing import Annotated

import marshmallow_recipe as mr

InstrumentId = int
UserId = int
CountryId = int
TagId = uuid.UUID
CompanyId = int
AccountId = uuid.UUID
MerchantId = uuid.UUID
TransactionId = uuid.UUID
ReminderMarkerId = uuid.UUID


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZenmoneyDiff:
    server_timestamp: int
    accounts: list[Account] = dataclasses.field(default_factory=list)
    companies: list[ZmCompany] = dataclasses.field(default_factory=list)
    countries: list[ZmCountry] = dataclasses.field(default_factory=list)
    instruments: list[ZmInstrument] = dataclasses.field(default_factory=list)
    merchants: list[ZmMerchant] = dataclasses.field(default_factory=list)
    tags: list[ZmTag] = dataclasses.field(default_factory=list)
    transactions: list[Transaction] = dataclasses.field(default_factory=list)
    users: list[ZmUser] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Account:
    id: AccountId
    changed: datetime.datetime
    user: UserId
    instrument: InstrumentId
    title: str
    role: int | None = None
    company: CompanyId | None = None
    type: str
    sync_id: list[str]
    balance: decimal.Decimal
    start_balance: decimal.Decimal
    credit_limit: decimal.Decimal
    in_balance: bool
    savings: bool
    enable_correction: bool
    enable_sms: bool
    archive: bool
    private: bool
    capitalization: str | None = None
    percent: decimal.Decimal | None = None
    start_date: datetime.datetime | None = None
    end_date_offset: int | None = None
    end_date_offset_interval: str | None = None
    payoff_step: int | None = None
    payoff_interval: str | None = None
    balance_correction_type: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Transaction:
    id: TransactionId
    changed: datetime.datetime
    created: datetime.datetime
    user: UserId
    deleted: bool
    hold: bool | None = None
    viewed: bool
    qr_code: str | None = None
    income_bank: str | None = None
    income_instrument: InstrumentId
    income_account: AccountId
    income: decimal.Decimal
    outcome_bank: str | None = None
    outcome_instrument: InstrumentId
    outcome_account: AccountId
    outcome: decimal.Decimal
    merchant: MerchantId | None = None
    payee: str | None = None
    original_payee: str | None = None
    comment: str | None = None
    date: datetime.date
    mcc: int | None = None
    reminder_marker: ReminderMarkerId | None = None
    op_income: decimal.Decimal | None = None
    op_income_instrument: InstrumentId | None = None
    op_outcome: decimal.Decimal | None = None
    op_outcome_instrument: InstrumentId | None = None
    latitude: float | None = None
    longitude: float | None = None
    source: str | None = None
    tags: list[TagId]


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
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


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmTag:
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


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmInstrument:
    id: Annotated[InstrumentId, mr.meta(description="Unique identifier of the instrument")]
    changed: Annotated[
        datetime.datetime,
        mr.datetime_meta(format="timestamp"),
        mr.meta(description="Last modification timestamp"),
    ]
    title: Annotated[str, mr.meta(description="Instrument title")]
    short_title: Annotated[str, mr.meta(description="Short instrument title")]
    symbol: Annotated[str, mr.meta(description="Instrument symbol")]
    rate: Annotated[decimal.Decimal, mr.meta(description="Exchange rate relative to the base instrument")]


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
class ZmMerchant:
    id: Annotated[MerchantId, mr.meta(description="Unique identifier of the merchant")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this merchant")]
    title: Annotated[str, mr.meta(description="Name of the merchant")]
