from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import ZmInstrument
from finstats.http.context import ErrorResponse, get_engine
from finstats.store.instruments import get_instruments


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetInstrumentsResponse:
    instruments: Annotated[list[ZmInstrument], mr.meta(description="List of instrument objects")]


class InstrumentsController(web.View):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Instruments"], summary="Get instruments", operationId="instrumentsList")
    @aiohttp_apigami.response_schema(mr.schema(GetInstrumentsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        engine = get_engine(self.request)

        async with engine.begin() as conn:
            instruments = await get_instruments(connection=conn)

        response = GetInstrumentsResponse(instruments)
        return web.json_response(mr.dump(response))
