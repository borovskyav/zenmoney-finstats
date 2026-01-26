from __future__ import annotations

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from client import ErrorResponse
from client.account import GetAccountsQueryData, GetAccountsResponse
from finstats.server.base import BaseController
from finstats.server.convert import accounts_to_account_models


class AccountsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Accounts"], summary="Get accounts", operationId="accountsList")
    @aiohttp_apigami.querystring_schema(mr.schema(GetAccountsQueryData))
    @aiohttp_apigami.response_schema(mr.schema(GetAccountsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 400)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        query_data = self.parse_request_query(GetAccountsQueryData)
        repository = self.get_accounts_repository()
        accounts = await repository.find_accounts(query_data.show_archive, query_data.show_debts)
        return web.json_response(mr.dump(GetAccountsResponse(accounts_to_account_models(accounts))))
