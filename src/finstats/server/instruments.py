from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.server.base import BaseController, ErrorResponse
from finstats.server.convert import instruments_to_instrument_models
from finstats.server.models import InstrumentModel


@dataclasses.dataclass(frozen=True, slots=True)
class GetInstrumentsResponse:
    instruments: Annotated[list[InstrumentModel], mr.meta(description="List of instrument objects")]


class InstrumentsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Instruments"], summary="Get instruments", operationId="instrumentsList")
    @aiohttp_apigami.response_schema(mr.schema(GetInstrumentsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        repository = self.get_instruments_repository()
        instruments = await repository.get_instruments()
        instrument_models = instruments_to_instrument_models(instruments)
        return web.json_response(mr.dump(GetInstrumentsResponse(instrument_models)))
