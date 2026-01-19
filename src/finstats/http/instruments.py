from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.domain import ZmInstrument
from finstats.http.base import BaseController, ErrorResponse


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetInstrumentsResponse:
    instruments: Annotated[list[ZmInstrument], mr.meta(description="List of instrument objects")]


class InstrumentsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Instruments"], summary="Get instruments", operationId="instrumentsList")
    @aiohttp_apigami.response_schema(mr.schema(GetInstrumentsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        repository = self.get_instruments_repository()
        instruments = await repository.get_instruments()
        return web.json_response(mr.dump(GetInstrumentsResponse(instruments)))
