from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apispec
import marshmallow_recipe as mr
from aiohttp import web

from finstats.http.context import ErrorResponse, get_engine
from finstats.store.psql_store import get_last_timestamp


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class HealthResponse:
    api: Annotated[str, mr.meta(description="API service status")]
    last_synced_timestamp: Annotated[str, mr.meta(description="Unix timestamp of the last successful data synchronization")]


class HealthController(web.View):
    @aiohttp_apispec.docs(tags=["Health"], summary="Get server health", operationId="serviceHealth")
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
