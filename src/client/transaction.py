import dataclasses
import datetime
import decimal
import enum
from typing import Annotated

import marshmallow_recipe as mr

from client.models import AccountId, InstrumentId, MerchantId, ReminderMarkerId, TagId, TransactionId, UserId


class TransactionType(enum.StrEnum):
    Income = "Income"
    Expense = "Expense"
    Transfer = "Transfer"
    DebtRepaid = "DebtRepaid"
    LentOut = "LentOut"
    ReturnIncome = "ReturnIncome"
    ReturnExpense = "ReturnExpense"


@dataclasses.dataclass(frozen=True, slots=True)
class GetTransactionsResponse:
    limit: Annotated[int, mr.meta(description="Maximum number of transactions returned in this response")]
    offset: Annotated[int, mr.meta(description="Number of records skipped from the beginning")]
    total_count: Annotated[int, mr.meta(description="Total number of transactions matching the query filters")]
    transactions: Annotated[list[TransactionModel], mr.meta(description="List of transaction objects")]


@dataclasses.dataclass(frozen=True, slots=True)
class GetTransactionsQueryData:
    offset: Annotated[int, mr.meta(description="Number of records to skip for pagination")] = 0
    limit: Annotated[int, mr.meta(description="Maximum number of transactions to return (max: 100)")] = 100
    from_date: Annotated[datetime.date | None, mr.meta(description="Filter transactions starting from this date (inclusive)")] = None
    to_date: Annotated[datetime.date | None, mr.meta(description="Filter transactions up to this date (inclusive)")] = None
    not_viewed: Annotated[bool, mr.meta(description="Filter only transactions that have not been viewed yet")] = False
    account_id: Annotated[AccountId | None, mr.meta(description="Filter transactions by account ID (matches either income or outcome account)")] = (
        None
    )
    tags: Annotated[
        list[TagId] | None,
        mr.list_meta(description="Filter transactions by tags (returns transactions that have at least one tag matching any from the provided list)"),
    ] = None
    transaction_type: Annotated[TransactionType, mr.meta(description="Filter transactions by transaction type: Income, Expense, Transfer")] = (
        mr.MISSING
    )


@dataclasses.dataclass(frozen=True, slots=True)
class PostCreateExpenseRequestBody:
    transaction_id: Annotated[TransactionId, mr.meta(description="Transaction ID. Must be unique. Generate a new UUID for each transaction.")]
    account_id: Annotated[AccountId, mr.meta(description="Source account ID. Resolve via accountsList by name.")]
    tag_id: Annotated[TagId, mr.meta(description="Tag/category ID. Resolve via tagsList by name.")]
    amount: Annotated[
        decimal.Decimal,
        mr.meta(
            description="Expense amount as a positive number.",
            validate=mr.validate(lambda x: x > 0, error="Expense amount cannot be negative"),
        ),
    ]
    merchant_id: Annotated[MerchantId | None, mr.meta(description="Merchant ID. Resolve via merchantsList by title. Optional.")] = None
    merchant_name: Annotated[str | None, mr.meta(description="Merchant name as text if merchant ID not found. Optional.")] = None
    comment: Annotated[str | None, mr.meta(description="Free-form note. Optional.")] = None
    date: Annotated[datetime.date | None, mr.datetime_meta(format="%Y-%m-%d", description="Date YYYY-MM-DD. Defaults to today if omitted.")] = None


@dataclasses.dataclass(frozen=True, slots=True)
class PostCreateIncomeRequestBody:
    transaction_id: Annotated[TransactionId, mr.meta(description="Transaction ID. Must be unique. Generate a new UUID for each transaction.")]
    account_id: Annotated[AccountId, mr.meta(description="Destination account ID. Resolve via accountsList by name.")]
    tag_id: Annotated[TagId, mr.meta(description="Tag/category ID. Resolve via tagsList by name.")]
    amount: Annotated[
        decimal.Decimal,
        mr.meta(
            description="Income amount as a positive number.",
            validate=mr.validate(lambda x: x > 0, error="Income amount cannot be negative"),
        ),
    ]
    merchant_id: Annotated[MerchantId | None, mr.meta(description="Merchant ID. Resolve via merchantsList by title. Optional.")] = None
    merchant_name: Annotated[str | None, mr.meta(description="Merchant name as text if merchant ID not found. Optional.")] = None
    comment: Annotated[str | None, mr.meta(description="Free-form note. Optional.")] = None
    date: Annotated[datetime.date | None, mr.datetime_meta(format="%Y-%m-%d", description="Date YYYY-MM-DD. Defaults to today if omitted.")] = None


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
