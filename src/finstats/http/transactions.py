from __future__ import annotations

import dataclasses
import datetime
from typing import Annotated

import aiohttp_apispec
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import ZmTransaction
from finstats.http.context import ErrorResponse, error_response_json, get_engine
from finstats.store.psql_store import get_transactions


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetTransactionsResponse:
    limit: Annotated[int, mr.meta(description="Maximum number of transactions returned in this response")]
    offset: Annotated[int, mr.meta(description="Number of records skipped from the beginning")]
    total_count: Annotated[int, mr.meta(description="Total number of transactions matching the query filters")]
    transactions: Annotated[list[ZmTransaction], mr.meta(description="List of transaction objects")]


@dataclasses.dataclass(frozen=True, slots=True)
class GetTransactionsQueryData:
    offset: Annotated[int, mr.meta(description="Number of records to skip for pagination")] = 0
    limit: Annotated[int, mr.meta(description="Maximum number of transactions to return (max: 100)")] = 100
    from_date: Annotated[datetime.date | None, mr.meta(description="Filter transactions starting from this date (inclusive)")] = None
    to_date: Annotated[datetime.date | None, mr.meta(description="Filter transactions up to this date (inclusive)")] = None
    not_viewed: Annotated[bool, mr.meta(description="Filter only transactions that have not been viewed yet")] = False


class TransactionsController(web.View):
    @aiohttp_apispec.docs(security=[{"BearerAuth": []}])
    @aiohttp_apispec.docs(tags=["Transactions"], summary="Get transactions", operationId="transactionsList")
    @aiohttp_apispec.querystring_schema(mr.schema(GetTransactionsQueryData))
    @aiohttp_apispec.response_schema(mr.schema(GetTransactionsResponse), 200)
    @aiohttp_apispec.response_schema(mr.schema(ErrorResponse), 400)
    @aiohttp_apispec.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apispec.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        query_data = self.parse_and_validate_get_query_params(self.request)
        engine = get_engine(self.request)

        async with engine.begin() as conn:
            transactions, total = await get_transactions(
                conn,
                limit=query_data.limit,
                offset=query_data.offset,
                from_date=query_data.from_date,
                to_date=query_data.to_date,
                not_viewed=query_data.not_viewed,
            )

        response = GetTransactionsResponse(
            transactions=transactions,
            limit=query_data.limit,
            offset=query_data.offset,
            total_count=total,
        )

        return web.json_response(mr.dump(response))

    def parse_and_validate_get_query_params(self, request: web.Request) -> GetTransactionsQueryData:
        try:
            query_data = mr.load(GetTransactionsQueryData, dict(request.query))
        except mr.ValidationError:
            raise web.HTTPBadRequest(text=error_response_json("failed to parse query"), content_type="application/json") from None

        if query_data.limit <= 0 or query_data.limit > 100:
            raise web.HTTPBadRequest(reason="limit cannot be negative or bigger than 100")
        if query_data.offset < 0:
            raise web.HTTPBadRequest(reason="offset cannot be negative")
        if query_data.from_date is not None and query_data.to_date is not None and query_data.from_date > query_data.to_date:
            raise web.HTTPBadRequest(reason="from_date cannot be greater than to_date")

        return query_data
