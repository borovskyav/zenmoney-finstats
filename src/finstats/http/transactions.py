from __future__ import annotations

import dataclasses
import datetime
import enum
import uuid
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import AccountId, InstrumentId, MerchantId, TagId, ZmTransaction
from finstats.http.context import BaseController, ErrorResponse


class TransactionType(enum.StrEnum):
    Income = "Income"
    Expense = "Expense"
    Transfer = "Transfer"
    DebtRepaid = "DebtRepaid"
    LentOut = "LentOut"


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetTransactionsResponse:
    limit: Annotated[int, mr.meta(description="Maximum number of transactions returned in this response")]
    offset: Annotated[int, mr.meta(description="Number of records skipped from the beginning")]
    total_count: Annotated[int, mr.meta(description="Total number of transactions matching the query filters")]
    transactions: Annotated[list[TransactionModel], mr.meta(description="List of transaction objects")]


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class TransactionModel(ZmTransaction):
    tags_titles: Annotated[list[str], mr.meta(description="Human-readable titles for the tags field, in the same order as IDs in tags")]
    income_instrument_title: Annotated[str, mr.meta(description="Human-readable title for the incomeInstrument field")]
    outcome_instrument_title: Annotated[str, mr.meta(description="Human-readable title for the outcomeInstrument field")]
    income_account_title: Annotated[str, mr.meta(description="Human-readable title for the incomeAccount field")]
    outcome_account_title: Annotated[str, mr.meta(description="Human-readable title for the outcomeAccount field")]
    merchant_title: Annotated[str | None, mr.meta(description="Human-readable title for the merchant field")]
    transaction_type: Annotated[TransactionType, mr.meta(description="Computed transaction type: Income, Expense, Transfer, DebtRepaid, or LentOut")]


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
        list[uuid.UUID] | None,
        mr.list_meta(description="Filter transactions by tags (returns transactions that have at least one tag matching any from the provided list)"),
    ] = None


class TransactionsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Transactions"], summary="Get transactions", operationId="transactionsList")
    @aiohttp_apigami.querystring_schema(mr.schema(GetTransactionsQueryData))
    @aiohttp_apigami.response_schema(mr.schema(GetTransactionsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 400)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        query_data = self.parse_and_validate_get_query_params(self.request)
        repository = self.get_transactions_repository()
        transactions, total = await repository.get_transactions(
            limit=query_data.limit,
            offset=query_data.offset,
            from_date=query_data.from_date,
            to_date=query_data.to_date,
            not_viewed=query_data.not_viewed,
            account_id=query_data.account_id,
            tags=query_data.tags,
        )
        enriched = await self.enrich_transactions(transactions)

        response = GetTransactionsResponse(
            transactions=enriched,
            limit=query_data.limit,
            offset=query_data.offset,
            total_count=total,
        )

        dump = mr.dump(response)
        return web.json_response(dump)

    async def enrich_transactions(self, transactions: list[ZmTransaction]) -> list[TransactionModel]:
        tags_set: set[TagId] = set()
        instrument_set: set[InstrumentId] = set()
        account_set: set[AccountId] = set()
        merchants_set: set[MerchantId] = set()
        for transaction in transactions:
            for tag in transaction.tags:
                tags_set.add(tag)

            instrument_set.add(transaction.income_instrument)
            instrument_set.add(transaction.outcome_instrument)
            account_set.add(transaction.income_account)
            account_set.add(transaction.outcome_account)
            if transaction.merchant:
                merchants_set.add(transaction.merchant)

        tags = await self.get_tags_repository().get_tags_by_id(tag_ids=list(tags_set))
        accounts = await self.get_accounts_repository().get_accounts_by_id(account_ids=list(account_set))
        instruments = await self.get_instruments_repository().get_instruments_by_id(instrument_ids=list(instrument_set))
        merchants = await self.get_merchants_repository().get_merchants_by_id(merchant_ids=list(merchants_set))

        tags_dict = {obj.id: obj for obj in tags}
        accounts_dict = {obj.id: obj for obj in accounts}
        instrument_dict = {obj.id: obj for obj in instruments}
        merchants_dict = {obj.id: obj for obj in merchants}

        transaction_models: list[TransactionModel] = []
        for transaction in transactions:
            tag_list: list[str] = []
            for tag in transaction.tags:
                tag_list.append("NO TAG TITLE" if tags_dict.get(tag) is None else tags_dict[tag].title)

            income_instrument_title = (
                "NO INSTRUMENT TITLE"
                if instrument_dict.get(transaction.income_instrument) is None
                else instrument_dict[transaction.income_instrument].title
            )
            outcome_instrument_title = (
                "NO INSTRUMENT TITLE"
                if instrument_dict.get(transaction.outcome_instrument) is None
                else instrument_dict[transaction.outcome_instrument].title
            )
            income_account = accounts_dict.get(transaction.income_account)
            outcome_account = accounts_dict.get(transaction.outcome_account)
            income_account_title = "NO ACCOUNT TITLE" if income_account is None else income_account.title
            outcome_account_title = "NO ACCOUNT TITLE" if outcome_account is None else outcome_account.title

            transaction_type = TransactionsController.calculate_transaction_type(
                transaction,
                income_account_type=income_account.type if income_account else None,
                outcome_account_type=outcome_account.type if outcome_account else None,
            )

            transaction_models.append(
                TransactionModel(
                    **dataclasses.asdict(transaction),
                    tags_titles=tag_list,
                    income_instrument_title=income_instrument_title,
                    outcome_instrument_title=outcome_instrument_title,
                    income_account_title=income_account_title,
                    outcome_account_title=outcome_account_title,
                    merchant_title=None if merchants_dict.get(transaction.merchant) is None else merchants_dict[transaction.merchant].title,
                    transaction_type=transaction_type,
                )
            )
        return transaction_models

    @staticmethod
    def calculate_transaction_type(
        transaction: ZmTransaction,
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

    @staticmethod
    def parse_and_validate_get_query_params(request: web.Request) -> GetTransactionsQueryData:
        try:
            query_dict = dict(request.query)
            if "tags" in request.query:
                query_dict["tags"] = request.query.getall("tags")
            query_data = mr.load(GetTransactionsQueryData, query_dict)
        except mr.ValidationError as e:
            raise web.HTTPBadRequest(reason=f"failed to parse query params: {e.normalized_messages()}") from None

        if query_data.limit <= 0 or query_data.limit > 100:
            raise web.HTTPBadRequest(reason="limit cannot be negative or bigger than 100")
        if query_data.offset < 0:
            raise web.HTTPBadRequest(reason="offset cannot be negative")
        if query_data.from_date is not None and query_data.to_date is not None and query_data.from_date > query_data.to_date:
            raise web.HTTPBadRequest(reason="from_date cannot be greater than to_date")

        return query_data
