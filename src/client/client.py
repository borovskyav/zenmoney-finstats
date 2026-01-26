from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator
from typing import LiteralString

import aio_request
import aiohttp
import marshmallow_recipe as mr
import yarl
from aio_request import Response

from client import AccountModel, InstrumentModel, TagModel
from client.account import GetAccountsQueryData, GetAccountsResponse
from client.health import HealthResponse
from client.instrument import GetInstrumentsResponse
from client.merchant import GetMerchantsResponse, MerchantModel
from client.models import ErrorResponse
from client.tag import GetTagsResponse
from client.transaction import GetTransactionsQueryData, GetTransactionsResponse


class FinstatsClient:
    __slots__ = ("__client", "__token")

    def __init__(self, session: aiohttp.ClientSession, base_url: yarl.URL, token: str) -> None:
        self.__client = aio_request.setup(
            transport=aio_request.AioHttpTransport(session),  # ty:ignore[possibly-missing-attribute]
            endpoint=base_url,
        )
        self.__token = token

    async def health(self) -> bool:
        response_ctx = self.__get(url="/health")
        async with response_ctx as response:
            response_body = await self.__handle_response(HealthResponse, response)
            return response_body.api == "ok"

    async def get_transactions(self, token: str | None = None) -> GetTransactionsResponse:
        response_ctx = self.__get(
            url="/api/v1/transactions",
            query=GetTransactionsQueryData(),
            token=token,
        )

        async with response_ctx as response:
            return await self.__handle_response(GetTransactionsResponse, response)

    async def get_accounts(
        self,
        show_archive: bool = False,
        show_debts: bool = False,
        token: str | None = None,
    ) -> list[AccountModel]:
        query = GetAccountsQueryData(show_archive=show_archive, show_debts=show_debts)
        response_ctx = self.__get(url="/api/v1/accounts", query=query, token=token)
        async with response_ctx as response:
            return (await self.__handle_response(GetAccountsResponse, response)).accounts

    async def get_tags(self, token: str | None = None) -> list[TagModel]:
        response_ctx = self.__get(url="/api/v1/tags", token=token)
        async with response_ctx as response:
            return (await self.__handle_response(GetTagsResponse, response)).tags

    async def get_instruments(self, token: str | None = None) -> list[InstrumentModel]:
        response_ctx = self.__get(url="/api/v1/instruments", token=token)
        async with response_ctx as response:
            return (await self.__handle_response(GetInstrumentsResponse, response)).instruments

    async def get_merchants(self, token: str | None = None) -> list[MerchantModel]:
        response_ctx = self.__get(url="/api/v1/merchants", token=token)
        async with response_ctx as response:
            return (await self.__handle_response(GetMerchantsResponse, response)).merchants

    @contextlib.asynccontextmanager
    async def __get(
        self,
        url: LiteralString,
        query: object | None = None,
        token: str | None = None,
    ) -> AsyncIterator[Response]:
        response_ctx = self.__client.request(
            request=aio_request.get(
                url=url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": token or self.__token,
                },
                query_parameters=None if query is None else mr.dump(query),
            ),
            deadline=aio_request.Deadline.from_timeout(20),
        )
        async with response_ctx as response:
            yield response

    @staticmethod
    async def __handle_response[T](cls: type[T], response: Response) -> T:
        if not response.is_successful():
            error = await FinstatsClient.__try_parse_error_from_response(response)
            raise Exception(error)
        if not response.is_json:
            raise Exception("Not json response")

        data = await response.json()
        if not isinstance(data, dict):
            raise Exception("Expected JSON object")

        return mr.load(cls, data)

    @staticmethod
    async def __try_parse_error_from_response(response: Response) -> str:
        exc_str = f"status code is {response.status}"
        response_error: str | None = None

        try:
            if response.is_json:
                data = await response.json()
                response_error = mr.load(ErrorResponse, data).message
            else:
                response_error = await response.text(encoding="utf-8")
        except aiohttp.ClientResponseError:
            pass

        if response_error:
            exc_str += f" with response error: {response_error}"

        return exc_str
