import dataclasses
import json
from typing import Annotated

import marshmallow_recipe as mr
from aiohttp import web

from finstats.client import ZenMoneyClient
from finstats.store.accounts import AccountsRepository
from finstats.store.companies import CompaniesRepository
from finstats.store.connection import ConnectionScope
from finstats.store.countries import CountriesRepository
from finstats.store.instruments import InstrumentsRepository
from finstats.store.merchants import MerchantsRepository
from finstats.store.tags import TagsRepository
from finstats.store.timestamp import TimestampRepository
from finstats.store.transactions import TransactionsRepository
from finstats.store.users import UsersRepository


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ErrorResponse:
    message: Annotated[str, mr.meta(description="Error message describing what went wrong")]


def error_response_json(reason: str) -> str:
    return json.dumps(mr.dump(ErrorResponse(message=reason)), separators=(",", ":"), ensure_ascii=False)


class BaseController(web.View):
    def get_connection_scope(self) -> ConnectionScope:
        connection_scope = self.request.config_dict["connection_scope"]
        if connection_scope is None:
            raise web.HTTPInternalServerError(reason="No connection_scope found")
        return connection_scope

    def get_timestamp_repository(self) -> TimestampRepository:
        timestamp_repository = self.request.config_dict["timestamp_repository"]
        if timestamp_repository is None:
            raise web.HTTPInternalServerError(reason="No timestamp_repository found")
        return timestamp_repository

    def get_accounts_repository(self) -> AccountsRepository:
        accounts_repository = self.request.config_dict["accounts_repository"]
        if accounts_repository is None:
            raise web.HTTPInternalServerError(reason="No accounts_repository found")
        return accounts_repository

    def get_instruments_repository(self) -> InstrumentsRepository:
        instruments_repository = self.request.config_dict["instruments_repository"]
        if instruments_repository is None:
            raise web.HTTPInternalServerError(reason="No instruments_repository found")
        return instruments_repository

    def get_tags_repository(self) -> TagsRepository:
        tags_repository = self.request.config_dict["tags_repository"]
        if tags_repository is None:
            raise web.HTTPInternalServerError(reason="No tags_repository found")
        return tags_repository

    def get_transactions_repository(self) -> TransactionsRepository:
        transactions_repository = self.request.config_dict["transactions_repository"]
        if transactions_repository is None:
            raise web.HTTPInternalServerError(reason="No transactions_repository found")
        return transactions_repository

    def get_users_repository(self) -> UsersRepository:
        users_repository = self.request.config_dict["users_repository"]
        if users_repository is None:
            raise web.HTTPInternalServerError(reason="No users_repository found")
        return users_repository

    def get_companies_repository(self) -> CompaniesRepository:
        companies_repository = self.request.config_dict["companies_repository"]
        if companies_repository is None:
            raise web.HTTPInternalServerError(reason="No companies_repository found")
        return companies_repository

    def get_countries_repository(self) -> CountriesRepository:
        countries_repository = self.request.config_dict["countries_repository"]
        if countries_repository is None:
            raise web.HTTPInternalServerError(reason="No countries_repository found")
        return countries_repository

    def get_merchants_repository(self) -> MerchantsRepository:
        merchants_repository = self.request.config_dict["merchants_repository"]
        if merchants_repository is None:
            raise web.HTTPInternalServerError(reason="No merchants_repository found")
        return merchants_repository

    def get_client(self) -> ZenMoneyClient:
        return get_client(self.request)

    def get_token(self) -> str:
        return get_token(self.request)


def get_client(request: web.Request) -> ZenMoneyClient:
    client = request.config_dict["client"]
    if client is None:
        raise web.HTTPInternalServerError(reason="No client found")
    return client


def get_token(request: web.Request) -> str:
    token = request.headers.get("Authorization")
    if not token:
        raise web.HTTPUnauthorized(reason="No Authorization token")
    return token
