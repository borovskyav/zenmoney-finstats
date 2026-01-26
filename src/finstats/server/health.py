from __future__ import annotations

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from client import ErrorResponse
from client.health import HealthResponse
from finstats.server.base import BaseController


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
