from __future__ import annotations

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from client import ErrorResponse
from client.merchant import GetMerchantsResponse
from finstats.server.base import BaseController
from finstats.server.convert import merchants_to_merchant_models


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
