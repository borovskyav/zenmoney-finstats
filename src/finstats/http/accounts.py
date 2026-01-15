from __future__ import annotations

import dataclasses
from typing import Annotated

import aiohttp_apigami
import marshmallow_recipe as mr
from aiohttp import web

from finstats.contracts import ZmAccount
from finstats.http.context import BaseController, ErrorResponse


@dataclasses.dataclass(frozen=True, slots=True)
class GetAccountsQueryData:
    show_archive: Annotated[bool, mr.meta(description="Include archived accounts in the response")] = False
    show_debts: Annotated[bool, mr.meta(description="Include debt/loan accounts in the response")] = False


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class GetAccountsResponse:
    accounts: Annotated[list[ZmAccount], mr.meta(description="List of account objects")]


class AccountsController(BaseController):
    @aiohttp_apigami.docs(security=[{"BearerAuth": []}])
    @aiohttp_apigami.docs(tags=["Accounts"], summary="Get accounts", operationId="accountsList")
    @aiohttp_apigami.querystring_schema(mr.schema(GetAccountsQueryData))
    @aiohttp_apigami.response_schema(mr.schema(GetAccountsResponse), 200)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 400)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 401)
    @aiohttp_apigami.response_schema(mr.schema(ErrorResponse), 500)
    async def get(self) -> web.StreamResponse:
        query_data = self.parse_and_validate_get_query_params(self.request)
        repository = self.get_accounts_repository()
        accounts = await repository.get_accounts(
            show_archive=query_data.show_archive,
            show_debts=query_data.show_debts,
        )
        return web.json_response(mr.dump(GetAccountsResponse(accounts)))

    @staticmethod
    def parse_and_validate_get_query_params(request: web.Request) -> GetAccountsQueryData:
        try:
            query_data = mr.load(GetAccountsQueryData, dict(request.query))
        except mr.ValidationError as e:
            raise web.HTTPBadRequest(reason=f"failed to parse query params: {e.normalized_messages()}") from None

        return query_data
