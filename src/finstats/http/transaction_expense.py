from __future__ import annotations

import dataclasses
import datetime
import decimal
import uuid
from typing import Annotated

import aiohttp_apigami as apispec
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import AccountId, InstrumentId, MerchantId, TagId, UserId, ZmMerchant, ZmTransaction
from finstats.http.context import BaseController, ErrorResponse
from finstats.http.openapi import OPENAI_EXT
from finstats.http.transactions import TransactionModel, TransactionsController


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class CreateExpenseRequest:
    idempotency_key: Annotated[uuid.UUID, mr.meta(description="Unique key to prevent duplicate transactions. Generate a new for each request.")]
    account_id: Annotated[AccountId, mr.meta(description="Source account ID. Resolve via accountsList by name.")]
    tag_id: Annotated[TagId, mr.meta(description="Tag/category ID. Resolve via tagsList by name.")]
    amount: Annotated[decimal.Decimal, mr.meta(description="Expense amount as a positive number.")]
    merchant_id: Annotated[MerchantId | None, mr.meta(description="Merchant ID. Resolve via merchantsList by title. Optional.")] = None
    merchant_name: Annotated[str | None, mr.meta(description="Merchant name as text if merchant ID not found. Optional.")] = None
    comment: Annotated[str | None, mr.meta(description="Free-form note. Optional.")] = None
    date: Annotated[datetime.date | None, mr.datetime_meta(format="%Y-%m-%d", description="Date YYYY-MM-DD. Defaults to today if omitted.")] = None


class ExpenseTransactionsController(BaseController):
    @apispec.docs(security=[{"BearerAuth": []}])
    @apispec.docs(tags=["Transactions"], summary="Create expense transaction", operationId="createExpense", **OPENAI_EXT)
    @apispec.json_schema(mr.schema(CreateExpenseRequest))
    @apispec.response_schema(mr.schema(TransactionModel), 200, description="Transaction created successfully, but not appeared in the service")
    @apispec.response_schema(mr.schema(TransactionModel), 201, description="Transaction created successfully")
    @apispec.response_schema(mr.schema(ErrorResponse), 400)
    @apispec.response_schema(mr.schema(ErrorResponse), 401)
    @apispec.response_schema(mr.schema(ErrorResponse), 500)
    async def post(self) -> web.StreamResponse:
        request = await self.parse_and_validate_request_body(self.request)

        user = await self.get_users_repository().get_user()
        account = await self.get_accounts_repository().get_account(request.account_id)
        if account is None:
            raise web.HTTPNotFound(reason="Account not found")
        tag = await self.get_tags_repository().get_tag(request.tag_id)
        if tag is None:
            raise web.HTTPNotFound(reason="Tag not found")
        merchant = None if request.merchant_id is None else await self.get_merchants_repository().get_merchant_by_id(request.merchant_id)

        # TODO: use request.idempotency_key as transaction id
        request_transaction = _create_expense_transaction(
            user_id=user.id,
            from_account_id=account.id,
            from_account_instrument_id=account.instrument,
            amount=request.amount,
            merchant=merchant,
            merchant_name=request.merchant_name,
            comment=request.comment,
            date=datetime.date.today() if request.date is None else request.date,
            tag_id=tag.id,
        )
        response = await self.get_syncer().sync_diff(token=self.get_token(), transactions=[request_transaction])
        zm_transaction = request_transaction
        for tr in response.transaction:
            if tr.id == zm_transaction.id:
                zm_transaction = tr
                break

        instruments = await self.get_instruments_repository().get_instruments_by_id([account.instrument])
        if not instruments:
            raise web.HTTPInternalServerError(reason="Instrument not found")

        model = TransactionModel(
            **dataclasses.asdict(zm_transaction),
            tags_titles=[tag.title],
            income_instrument_title=instruments[0].title,
            outcome_instrument_title=instruments[0].title,
            income_account_title=account.title,
            outcome_account_title=account.title,
            merchant_title=None if not merchant else merchant.title,
            transaction_type=TransactionsController.calculate_transaction_type(
                transaction=zm_transaction,
                income_account_type=account.type,
                outcome_account_type=account.type,
            ),
        )

        return web.json_response(mr.dump(model))

    @staticmethod
    async def parse_and_validate_request_body(request: web.Request) -> CreateExpenseRequest:
        try:
            json_body = await request.json()
            body = mr.load(CreateExpenseRequest, json_body)
        except mr.ValidationError as e:
            raise web.HTTPBadRequest(reason=f"failed to parse query params: {e.normalized_messages()}") from None

        if body.amount <= 0:
            raise web.HTTPBadRequest(reason="amount must be positive") from None

        return body


def _create_expense_transaction(
    user_id: UserId,
    from_account_id: AccountId,
    from_account_instrument_id: InstrumentId,
    amount: decimal.Decimal,
    merchant: ZmMerchant | None,
    merchant_name: str | None,
    comment: str | None,
    date: datetime.date,
    tag_id: TagId,
) -> ZmTransaction:
    return ZmTransaction(
        id=uuid.uuid4(),
        changed=datetime.datetime.now(datetime.UTC),
        created=datetime.datetime.now(datetime.UTC),
        user=user_id,
        deleted=False,
        viewed=False,
        income_instrument=from_account_instrument_id,
        income_account=from_account_id,
        income=decimal.Decimal(0),  # check: из ZM -> 0, у нас -> "0.00"
        outcome_instrument=from_account_instrument_id,
        outcome_account=from_account_id,
        outcome=amount,
        merchant=merchant.id if merchant else None,
        payee=merchant.title if merchant else merchant_name,
        original_payee=merchant.title if merchant else merchant_name,
        comment=comment,
        date=date,
        tags=[tag_id],
    )
