from __future__ import annotations

import dataclasses
import datetime
import decimal
import uuid
from typing import Annotated

import aiohttp_apigami as apispec
import marshmallow_recipe as mr
from aiohttp import web

from finstats.domain import AccountId, InstrumentId, Merchant, MerchantId, TagId, Transaction, TransactionId, UserId
from finstats.server.base import BaseController, ErrorResponse
from finstats.server.convert import transaction_to_transaction_model
from finstats.server.models import TransactionModel, _calculate_transaction_type
from finstats.server.openapi import OPENAI_EXT


@dataclasses.dataclass(frozen=True, slots=True)
class CreateIncomeRequest:
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


class IncomeTransactionsController(BaseController):
    @apispec.docs(security=[{"BearerAuth": []}])
    @apispec.docs(tags=["Transactions"], summary="Create income transaction", operationId="createIncome", **OPENAI_EXT)
    @apispec.json_schema(mr.schema(CreateIncomeRequest))
    @apispec.response_schema(mr.schema(TransactionModel), 200, description="Transaction created successfully, but not appeared in the service")
    @apispec.response_schema(mr.schema(TransactionModel), 201, description="Transaction created successfully")
    @apispec.response_schema(mr.schema(ErrorResponse), 400)
    @apispec.response_schema(mr.schema(ErrorResponse), 401)
    @apispec.response_schema(mr.schema(ErrorResponse), 409, description="Transaction with same id already exists")
    @apispec.response_schema(mr.schema(ErrorResponse), 500)
    async def post(self) -> web.StreamResponse:
        request = await self.parse_request_body(CreateIncomeRequest)
        self.validate_request_body(request)

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
        if not tag.show_income:
            raise web.HTTPBadRequest(reason="Tag cannot be income")

        merchant = None if request.merchant_id is None else await self.get_merchants_repository().get_merchant_by_id(request.merchant_id)

        request_transaction = _create_income_transaction(
            transaction_id=request.transaction_id,
            user_id=user.id,
            to_account_id=account.id,
            to_account_instrument_id=account.instrument,
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
            transaction_type=_calculate_transaction_type(
                transaction=zm_transaction,
                income_account_type=account.type,
                outcome_account_type=account.type,
                tag=tag,
            ),
        )

        return web.json_response(mr.dump(model), status=status_code)

    @staticmethod
    def validate_request_body(body: CreateIncomeRequest) -> None:
        if body.amount <= 0:
            raise web.HTTPBadRequest(reason="amount must be positive") from None


def _create_income_transaction(
    transaction_id: uuid.UUID,
    user_id: UserId,
    to_account_id: AccountId,
    to_account_instrument_id: InstrumentId,
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
        income_instrument=to_account_instrument_id,
        income_account=to_account_id,
        income=amount,
        outcome_instrument=to_account_instrument_id,
        outcome_account=to_account_id,
        outcome=decimal.Decimal(0),
        merchant=merchant.id if merchant else None,
        payee=merchant.title if merchant else merchant_name,
        original_payee=merchant.title if merchant else merchant_name,
        comment=comment,
        date=date,
        tags=[tag_id],
    )
