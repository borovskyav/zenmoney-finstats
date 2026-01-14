from __future__ import annotations

import abc
import dataclasses
import datetime
import decimal
import uuid
from typing import Annotated, Any

import marshmallow_recipe as mr


class ZenMoneyClientException(Exception):
    pass


class ZenMoneyClientAuthException(ZenMoneyClientException):
    pass


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
class ZmAccount:
    id: Annotated[AccountId, mr.meta(description="Unique identifier of the account")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this account")]
    instrument: Annotated[InstrumentId, mr.meta(description="Currency/instrument ID for the account")]
    title: Annotated[str, mr.meta(description="Account title")]
    role: Annotated[int | None, mr.meta(description="Account role identifier from the source system")]
    company: Annotated[CompanyId | None, mr.meta(description="Company ID associated with the account")]
    type: Annotated[str, mr.meta(description="Account type")]
    sync_id: Annotated[list[str], mr.meta(name="syncID", description="External sync identifiers for the account")]
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
    capitalization: Annotated[str | None, mr.meta(description="Capitalization type for deposit/loan accounts")]
    percent: Annotated[decimal.Decimal | None, mr.meta(description="Interest rate for deposit/loan accounts")]
    start_date: Annotated[
        datetime.datetime | None,
        mr.datetime_meta(format="timestamp"),
        mr.meta(description="Start date for deposit/loan accounts"),
    ]
    end_date_offset: Annotated[int | None, mr.meta(description="End date offset value for deposit/loan accounts")]
    end_date_offset_interval: Annotated[str | None, mr.meta(description="End date offset interval unit")]
    payoff_step: Annotated[int | None, mr.meta(description="Payoff step value for loan accounts")]
    payoff_interval: Annotated[str | None, mr.meta(description="Payoff interval unit for loan accounts")]
    balance_correction_type: Annotated[str, mr.meta(description="Balance correction type")]

    @staticmethod
    @mr.pre_load
    def normalise_data(data: dict[str, Any]) -> dict[str, Any]:
        if "syncID" not in data or data.get("syncID") is None:
            data["syncID"] = []
        return data


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmMerchant:
    id: MerchantId
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp")]
    user: UserId
    title: str


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ZmTransaction:
    id: Annotated[TransactionId, mr.meta(description="Unique identifier of the transaction")]
    changed: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Last modification timestamp")]
    created: Annotated[datetime.datetime, mr.datetime_meta(format="timestamp"), mr.meta(description="Transaction creation timestamp")]
    user: Annotated[UserId, mr.meta(description="ID of the user who owns this transaction")]
    deleted: Annotated[bool, mr.meta(description="Whether the transaction has been deleted")]
    hold: Annotated[bool | None, mr.meta(description="Whether the transaction is on hold (pending)")]
    viewed: Annotated[bool, mr.meta(description="Whether the transaction has been viewed by the user")]
    qr_code: Annotated[str | None, mr.meta(description="QR code associated with the transaction")]
    income_bank: Annotated[str | None, mr.meta(name="incomeBankID", description="Bank ID for the income side of the transaction")]
    income_instrument: Annotated[InstrumentId, mr.meta(description="Currency/instrument ID for the income")]
    income_account: Annotated[AccountId, mr.meta(description="Account ID receiving the income")]
    income: Annotated[decimal.Decimal, mr.meta(description="Income amount in the income account's currency")]
    outcome_bank: Annotated[str | None, mr.meta(name="outcomeBankID", description="Bank ID for the outcome side of the transaction")]
    outcome_instrument: Annotated[InstrumentId, mr.meta(description="Currency/instrument ID for the outcome")]
    outcome_account: Annotated[AccountId, mr.meta(description="Account ID from which the outcome is withdrawn")]
    outcome: Annotated[decimal.Decimal, mr.meta(description="Outcome amount in the outcome account's currency")]
    merchant: Annotated[MerchantId | None, mr.meta(description="ID of the merchant associated with the transaction")]
    payee: Annotated[str | None, mr.meta(description="Name of the payee/recipient")]
    original_payee: Annotated[str | None, mr.meta(description="Original payee name before user modifications")]
    comment: Annotated[str | None, mr.meta(description="User's comment or note about the transaction")]
    date: Annotated[datetime.date, mr.meta(description="Transaction date")] = dataclasses.field(metadata=mr.datetime_meta(format="%Y-%m-%d"))
    mcc: Annotated[int | None, mr.meta(description="Merchant Category Code (MCC) for the transaction")]
    reminder_marker: Annotated[ReminderMarkerId | None, mr.meta(description="ID of the associated reminder marker")]
    op_income: Annotated[decimal.Decimal | None, mr.meta(description="Original income amount before currency conversion")]
    op_income_instrument: Annotated[InstrumentId | None, mr.meta(description="Original income currency/instrument ID")]
    op_outcome: Annotated[decimal.Decimal | None, mr.meta(description="Original outcome amount before currency conversion")]
    op_outcome_instrument: Annotated[InstrumentId | None, mr.meta(description="Original outcome currency/instrument ID")]
    latitude: Annotated[decimal.Decimal | None, mr.meta(description="Geographical latitude where the transaction occurred")]
    longitude: Annotated[decimal.Decimal | None, mr.meta(description="Geographical longitude where the transaction occurred")]
    source: Annotated[str | None, mr.meta(description="Source of the transaction (manual, import, sync, etc.)")]

    tags: Annotated[list[TagId], mr.meta(description="List of tag IDs associated with the transaction")] = dataclasses.field(
        default_factory=list, metadata=mr.list_meta(name="tag")
    )

    @staticmethod
    @mr.pre_load
    def normalise_data(data: dict[str, Any]) -> dict[str, Any]:
        if "outcomeAccount" not in data or data.get("outcomeAccount") is None:
            data["outcomeAccount"] = uuid.UUID("5c6d2ce9-4d67-450c-b40d-28a7dea1e20e")
        if "tag" not in data or data.get("tag") is None:
            data["tag"] = []
        return data


class DiffClient(abc.ABC):
    @abc.abstractmethod
    async def fetch_diff(self, token: str, server_timestamp: int, timeout_seconds: int = 20) -> ZmDiffResponse: ...
