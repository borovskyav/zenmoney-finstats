from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web


@dataclasses.dataclass(frozen=True, slots=True)
class HealthResponse:
    api: Annotated[str, mr.meta(description="API service status")]


class HealthController(web.View):
    @aiohttp_apigami.docs(tags=["Health"], summary="Get server health", operationId="serviceHealth")
    @aiohttp_apigami.response_schema(mr.schema(HealthResponse), 200)
    async def get(self) -> web.Response:
        return web.json_response(mr.dump(HealthResponse(api="ok")))
