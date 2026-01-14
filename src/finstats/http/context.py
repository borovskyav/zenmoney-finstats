import dataclasses
import json
from typing import Annotated

import marshmallow_recipe as mr
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncEngine

from finstats.client import ZenMoneyClient


@dataclasses.dataclass(frozen=True, slots=True)
@mr.options(naming_case=mr.CAMEL_CASE)
class ErrorResponse:
    message: Annotated[str, mr.meta(description="Error message describing what went wrong")]


def error_response_json(reason: str) -> str:
    return json.dumps(mr.dump(ErrorResponse(message=reason)), separators=(",", ":"), ensure_ascii=False)


def get_engine(request: web.Request) -> AsyncEngine:
    engine = request.config_dict["engine"]
    if engine is None:
        raise web.HTTPInternalServerError(reason="No engine found")
    return engine


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
