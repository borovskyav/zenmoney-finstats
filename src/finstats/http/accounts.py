from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.http.base import BaseController, ErrorResponse
from finstats.http.convert import accounts_to_account_models
from finstats.http.models import AccountModel


@dataclasses.dataclass(frozen=True, slots=True)
class GetAccountsQueryData:
    show_archive: Annotated[bool, mr.meta(description="Include archived accounts in the response")] = False
    show_debts: Annotated[bool, mr.meta(description="Include debt/loan accounts in the response")] = False


@dataclasses.dataclass(frozen=True, slots=True)
class GetAccountsResponse:
    accounts: Annotated[list[AccountModel], mr.meta(description="List of account objects")]


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
        accounts = await repository.get_accounts(query_data.show_archive, query_data.show_debts)
        return web.json_response(mr.dump(GetAccountsResponse(accounts_to_account_models(accounts))))
