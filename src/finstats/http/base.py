import dataclasses
import json
from typing import Annotated

import marshmallow_recipe as mr
from aiohttp import web

from finstats.client.client import ZenMoneyClient
from finstats.container import Container
from finstats.store import (
    AccountsRepository,
    CompaniesRepository,
    CountriesRepository,
    InstrumentsRepository,
    MerchantsRepository,
    TagsRepository,
    TimestampRepository,
    TransactionsRepository,
    UsersRepository,
)
from finstats.store.connection import ConnectionScope
from finstats.syncer import Syncer


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ErrorResponse:
    message: Annotated[str, mr.meta(description="Error message describing what went wrong")]


def error_response_json(reason: str) -> str:
    return json.dumps(mr.dump(ErrorResponse(message=reason)), separators=(",", ":"), ensure_ascii=False)


class BaseController(web.View):
    def get_connection_scope(self) -> ConnectionScope:
        return get_container(self.request).resolve(ConnectionScope)

    def get_timestamp_repository(self) -> TimestampRepository:
        return get_container(self.request).resolve(TimestampRepository)

    def get_accounts_repository(self) -> AccountsRepository:
        return get_container(self.request).resolve(AccountsRepository)

    def get_instruments_repository(self) -> InstrumentsRepository:
        return get_container(self.request).resolve(InstrumentsRepository)

    def get_tags_repository(self) -> TagsRepository:
        return get_container(self.request).resolve(TagsRepository)

    def get_transactions_repository(self) -> TransactionsRepository:
        return get_container(self.request).resolve(TransactionsRepository)

    def get_users_repository(self) -> UsersRepository:
        return get_container(self.request).resolve(UsersRepository)

    def get_companies_repository(self) -> CompaniesRepository:
        return get_container(self.request).resolve(CompaniesRepository)

    def get_countries_repository(self) -> CountriesRepository:
        return get_container(self.request).resolve(CountriesRepository)

    def get_merchants_repository(self) -> MerchantsRepository:
        return get_container(self.request).resolve(MerchantsRepository)

    def get_syncer(self) -> Syncer:
        return get_container(self.request).resolve(Syncer)

    def get_client(self) -> ZenMoneyClient:
        return get_client(self.request)

    def get_token(self) -> str:
        return get_token(self.request)

    def parse_request_query[T](self, cls: type[T], collect_query_params: set[str] | None = None) -> T:
        if collect_query_params is None:
            collect_query_params = set()

        query_dict = dict(self.request.query)
        for key in collect_query_params:
            if key in query_dict:
                query_dict[key] = self.request.query.getall(key)

        try:
            return mr.load(cls, query_dict)
        except mr.ValidationError as e:
            raise web.HTTPBadRequest(reason=f"failed to parse query params: {e.normalized_messages()}") from e

    async def parse_request_body[T](self, cls: type[T]) -> T:
        try:
            json_body = await self.request.json()
            return mr.load(cls, json_body)
        except mr.ValidationError as e:
            raise web.HTTPBadRequest(reason=f"failed to parse request body: {e.normalized_messages()}") from e


def get_client(request: web.Request) -> ZenMoneyClient:
    return get_container(request).resolve(ZenMoneyClient)


def get_token(request: web.Request) -> str:
    token = request.headers.get("Authorization")
    if not token:
        raise web.HTTPUnauthorized(reason="No Authorization token")
    return token


def get_container(request: web.Request) -> Container:
    container = request.config_dict["container"]
    if container is None:
        raise web.HTTPInternalServerError(reason="No client found")
    return container
