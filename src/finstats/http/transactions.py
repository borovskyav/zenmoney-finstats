from __future__ import annotations

import dataclasses
import datetime

import aiohttp_apispec
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import ZmTransaction
from finstats.http.context import ErrorResponse, error_response_json, get_engine
from finstats.store.psql_store import get_transactions


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetTransactionsResponse:
    transactions: list[ZmTransaction]
    limit: int
    offset: int
    total_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class GetTransactionsQueryData:
    offset: int = 0
    limit: int = 100
    from_date: datetime.date | None = None
    to_date: datetime.date | None = None


class TransactionsController(web.View):
    @aiohttp_apispec.docs(security=[{"BearerAuth": []}])
    @aiohttp_apispec.docs(tags=["Transactions"], summary="Get transactions")
    @aiohttp_apispec.querystring_schema(mr.schema(GetTransactionsQueryData))
    @aiohttp_apispec.response_schema(mr.schema(GetTransactionsResponse), 200)
    @aiohttp_apispec.response_schema(mr.schema(ErrorResponse), 400)
    @aiohttp_apispec.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apispec.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        limit, offset, from_date, to_date = self.parse_and_validate_get_query_params(self.request)
        engine = get_engine(self.request)

        async with engine.begin() as conn:
            transactions, total = await get_transactions(
                conn, limit=limit, offset=offset, from_date=from_date, to_date=to_date
            )

        response = GetTransactionsResponse(
            transactions=transactions,
            limit=limit,
            offset=offset,
            total_count=total,
        )

        return web.json_response(mr.dump(response))

    def parse_and_validate_get_query_params(
        self, request: web.Request
    ) -> tuple[int, int, datetime.date | None, datetime.date | None]:
        try:
            query_data = mr.load(GetTransactionsQueryData, dict(request.query))
        except mr.ValidationError:
            raise web.HTTPBadRequest(
                text=error_response_json("failed to parse query"), content_type="application/json"
            ) from None

        if query_data.limit <= 0 or query_data.limit > 100:
            raise web.HTTPBadRequest(reason="limit cannot be negative or bigger than 100")
        if query_data.offset < 0:
            raise web.HTTPBadRequest(reason="offset cannot be negative")
        if (
            query_data.from_date is not None
            and query_data.to_date is not None
            and query_data.from_date > query_data.to_date
        ):
            raise web.HTTPBadRequest(reason="from_date cannot be greater than to_date")

        return query_data.limit, query_data.offset, query_data.from_date, query_data.to_date
