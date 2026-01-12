from __future__ import annotations

import dataclasses
import datetime

import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import ZmTransaction
from finstats.http.context import get_engine
from finstats.store.psql_store import get_transactions


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetTransactionsResponse:
    transactions: list[ZmTransaction]
    limit: int
    offset: int
    total_count: int


class TransactionsController(web.View):
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
        q = self.request.query
        limit = int(q.get("limit", "100"))
        offset = int(q.get("offset", "0"))

        from_date_s = q.get("from_date")
        to_date_s = q.get("to_date")
        from_date = datetime.date.fromisoformat(from_date_s) if from_date_s else None
        to_date = datetime.date.fromisoformat(to_date_s) if to_date_s else None

        if 0 > limit > 100:
            raise web.HTTPBadRequest(reason="limit cannot be negative")
        if offset < 0:
            raise web.HTTPBadRequest(reason="offset cannot be negative")
        if from_date is not None and to_date is not None and from_date > to_date:
            raise web.HTTPBadRequest(reason="from_date cannot be less than to_date")

        return limit, offset, from_date, to_date
