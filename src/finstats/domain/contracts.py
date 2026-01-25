from __future__ import annotations

import dataclasses
import datetime
import decimal
import enum
import uuid

InstrumentId = int
UserId = int
CountryId = int
TagId = uuid.UUID
CompanyId = int
AccountId = uuid.UUID
MerchantId = uuid.UUID
TransactionId = uuid.UUID
ReminderMarkerId = uuid.UUID


class TagType(enum.StrEnum):
    Income = "Income"
    Expense = "Expense"
    Both = "Both"


class TransactionType(enum.StrEnum):
    Income = "Income"
    Expense = "Expense"
    Transfer = "Transfer"
    DebtRepaid = "DebtRepaid"
    LentOut = "LentOut"
    ReturnIncome = "ReturnIncome"
    ReturnExpense = "ReturnExpense"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ZenmoneyDiff:
    server_timestamp: int
    accounts: list[Account] = dataclasses.field(default_factory=list)
    companies: list[Company] = dataclasses.field(default_factory=list)
    countries: list[Country] = dataclasses.field(default_factory=list)
    instruments: list[Instrument] = dataclasses.field(default_factory=list)
    merchants: list[Merchant] = dataclasses.field(default_factory=list)
    tags: list[Tag] = dataclasses.field(default_factory=list)
    transactions: list[Transaction] = dataclasses.field(default_factory=list)
    users: list[User] = dataclasses.field(default_factory=list)


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


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class User:
    id: UserId
    changed: datetime.datetime
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
    paid_till: datetime.datetime
    subscription: str | None  # '10yearssubscription' | '1MonthSubscription' | None
    subscription_renewal_date: str | None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Tag:
    id: TagId
    changed: datetime.datetime
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
class Instrument:
    id: InstrumentId
    changed: datetime.datetime
    title: str
    short_title: str
    symbol: str
    rate: decimal.Decimal


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Country:
    id: CountryId
    title: str
    currency: InstrumentId
    domain: str | None


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Merchant:
    id: MerchantId
    changed: datetime.datetime
    user: UserId
    title: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Company:
    id: CompanyId
    changed: datetime.datetime
    title: str
    full_title: str | None
    www: str | None
    country: CountryId | None
    country_code: str | None  # RU
    deleted: bool
