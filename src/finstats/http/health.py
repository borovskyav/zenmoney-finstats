from __future__ import annotations

import dataclasses

import aiohttp_apispec
import marshmallow_recipe as mr
from aiohttp import web

from finstats.http.context import ErrorResponse, get_engine
from finstats.store.psql_store import get_last_timestamp


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class HealthResponse:
    api: str
    last_synced_timestamp: str


class HealthController(web.View):
    @aiohttp_apispec.docs(tags=["Health"], summary="Get server health")
    @aiohttp_apispec.response_schema(mr.schema(HealthResponse), 200)
    @aiohttp_apispec.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.Response:
        engine = get_engine(self.request)
        last_timestamp: str = "0"

        try:
            async with engine.connect() as connection:
                last_timestamp = f"{await get_last_timestamp(connection)}"
        except Exception:
            last_timestamp = "psql is not available"

        return web.json_response(mr.dump(HealthResponse(api="ok", last_synced_timestamp=last_timestamp)))
