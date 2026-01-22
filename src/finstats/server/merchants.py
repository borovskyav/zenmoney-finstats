from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.server.base import BaseController, ErrorResponse
from finstats.server.convert import merchants_to_merchant_models
from finstats.server.models import MerchantModel


@dataclasses.dataclass(frozen=True, slots=True)
class GetMerchantsResponse:
    merchants: Annotated[list[MerchantModel], mr.meta(description="List of merchant objects")]


class MerchantsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Merchants"], summary="Get merchants", operationId="merchantsList")
    @aiohttp_apigami.response_schema(mr.schema(GetMerchantsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        repository = self.get_merchants_repository()
        merchants = await repository.get_merchants()
        merchant_models = merchants_to_merchant_models(merchants)
        return web.json_response(mr.dump(GetMerchantsResponse(merchant_models)))
