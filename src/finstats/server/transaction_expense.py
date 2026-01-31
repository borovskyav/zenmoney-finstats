from __future__ import annotations

import datetime
import decimal
import uuid

import aiohttp_apigami as apispec
import marshmallow_recipe as mr
from aiohttp import web

from client import ErrorResponse, TransactionModel
from client.transaction import PostCreateExpenseRequestBody
from finstats.domain import (
    AccountId,
    InstrumentId,
    Merchant,
    TagId,
    Transaction,
    UserId,
)
from finstats.server.base import BaseController
from finstats.server.convert import calculate_transaction_type, transaction_to_transaction_model
from finstats.server.openapi import OPENAI_EXT


class ExpenseTransactionsController(BaseController):
    @apispec.docs(security=[{"BearerAuth": []}])
    @apispec.docs(tags=["Transactions"], summary="Create expense transaction", operationId="createExpense", **OPENAI_EXT)
    @apispec.json_schema(mr.schema(PostCreateExpenseRequestBody))
    @apispec.response_schema(mr.schema(TransactionModel), 200, description="Transaction created successfully, but not appeared in the service")
    @apispec.response_schema(mr.schema(TransactionModel), 201, description="Transaction created successfully")
    @apispec.response_schema(mr.schema(ErrorResponse), 400)
    @apispec.response_schema(mr.schema(ErrorResponse), 401)
    @apispec.response_schema(mr.schema(ErrorResponse), 409, description="Transaction with same id already exists")
    @apispec.response_schema(mr.schema(ErrorResponse), 500)
    async def post(self) -> web.StreamResponse:
        request = await self.parse_request_body(PostCreateExpenseRequestBody)

        transaction = await self.get_transactions_repository().get_transaction(request.transaction_id)
        if transaction is not None:
            raise web.HTTPConflict(reason="Transaction with same id already exists")

        user = await self.get_users_repository().get_user()
        account = await self.get_accounts_repository().get_account(request.account_id)
        if account is None:
            raise web.HTTPNotFound(reason="Account not found")

        tag = await self.get_tags_repository().get_tag(request.tag_id)
        if tag is None:
            raise web.HTTPNotFound(reason="Tag not found")
        if not tag.show_outcome:
            raise web.HTTPBadRequest(reason="Tag cannot be outcome")

        merchant = None if request.merchant_id is None else await self.get_merchants_repository().get_merchant_by_id(request.merchant_id)

        request_transaction = _create_expense_transaction(
            transaction_id=request.transaction_id,
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
        status_code = 200
        for tr in response.transactions:
            if tr.id == zm_transaction.id:
                zm_transaction = tr
                status_code = 201
                break

        instruments = await self.get_instruments_repository().get_instruments_by_id([account.instrument])
        if not instruments:
            raise web.HTTPInternalServerError(reason="Instrument not found")

        model = transaction_to_transaction_model(
            transaction=zm_transaction,
            tags_titles=[tag.title],
            income_instrument_title=instruments[0].title,
            outcome_instrument_title=instruments[0].title,
            income_account_title=account.title,
            outcome_account_title=account.title,
            merchant_title=None if not merchant else merchant.title,
            transaction_type=calculate_transaction_type(
                transaction=zm_transaction,
                income_account_type=account.type,
                outcome_account_type=account.type,
                tag=tag,
            ),
        )

        return web.json_response(mr.dump(model), status=status_code)


def _create_expense_transaction(
    transaction_id: uuid.UUID,
    user_id: UserId,
    from_account_id: AccountId,
    from_account_instrument_id: InstrumentId,
    amount: decimal.Decimal,
    merchant: Merchant | None,
    merchant_name: str | None,
    comment: str | None,
    date: datetime.date,
    tag_id: TagId,
) -> Transaction:
    return Transaction(
        id=transaction_id,
        changed=datetime.datetime.now(datetime.UTC),
        created=datetime.datetime.now(datetime.UTC),
        user=user_id,
        deleted=False,
        viewed=False,
        income_instrument=from_account_instrument_id,
        income_account=from_account_id,
        income=decimal.Decimal(0.0),
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
