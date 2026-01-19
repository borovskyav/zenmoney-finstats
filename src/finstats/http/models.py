from __future__ import annotations

import dataclasses
import datetime
import decimal
import enum
from typing import Annotated

import marshmallow_recipe as mr

from finstats.domain import (
    AccountId,
    CompanyId,
    InstrumentId,
    MerchantId,
    ReminderMarkerId,
    TagId,
    Transaction,
    TransactionId,
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


class TransactionType(enum.StrEnum):
    Income = "Income"
    Expense = "Expense"
    Transfer = "Transfer"
    DebtRepaid = "DebtRepaid"
    LentOut = "LentOut"


def calculate_transaction_type(
    transaction: Transaction,
    income_account_type: str | None,
    outcome_account_type: str | None,
) -> TransactionType:
    if transaction.outcome == 0 and transaction.income > 0:
        return TransactionType.Income
    if transaction.income == 0 and transaction.outcome > 0:
        return TransactionType.Expense
    if transaction.income > 0 and transaction.outcome > 0:
        if income_account_type == "debt":
            return TransactionType.DebtRepaid
        if outcome_account_type == "debt":
            return TransactionType.LentOut
        return TransactionType.Transfer
    return TransactionType.Transfer
