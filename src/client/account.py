import dataclasses
import datetime
import decimal
from typing import Annotated

import marshmallow_recipe as mr

from client.models import AccountId, CompanyId, InstrumentId, UserId


@dataclasses.dataclass(frozen=True, slots=True)
class GetAccountsQueryData:
    show_archive: Annotated[bool, mr.meta(description="Include archived accounts in the response")] = False
    show_debts: Annotated[bool, mr.meta(description="Include debt/loan accounts in the response")] = False


@dataclasses.dataclass(frozen=True, slots=True)
class GetAccountsResponse:
    accounts: Annotated[list[AccountModel], mr.meta(description="List of account objects")]


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
