from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import ZmMerchant
from finstats.http.context import BaseController, ErrorResponse


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetMerchantsResponse:
    merchants: Annotated[list[ZmMerchant], mr.meta(description="List of merchant objects")]


class MerchantsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Merchants"], summary="Get merchants", operationId="merchantsList")
    @aiohttp_apigami.response_schema(mr.schema(GetMerchantsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        repository = self.get_merchants_repository()
        merchants = await repository.get_merchants()
        return web.json_response(mr.dump(GetMerchantsResponse(merchants)))
