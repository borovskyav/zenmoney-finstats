from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.http.base import BaseController, ErrorResponse


@dataclasses.dataclass(frozen=True, slots=True)
class HealthResponse:
    api: Annotated[str, mr.meta(description="API service status")]
    last_synced_timestamp: Annotated[str, mr.meta(description="Unix timestamp of the last successful data synchronization")]


class HealthController(BaseController):
    @aiohttp_apigami.docs(tags=["Health"], summary="Get server health", operationId="serviceHealth")
    @aiohttp_apigami.response_schema(mr.schema(HealthResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.Response:
        repository = self.get_timestamp_repository()
        try:
            last_timestamp = f"{await repository.get_last_timestamp()}"
            return web.json_response(mr.dump(HealthResponse(api="ok", last_synced_timestamp=last_timestamp)))
        except Exception:
            return web.json_response(mr.dump(HealthResponse(api="error", last_synced_timestamp="unavailable")), status=503)
