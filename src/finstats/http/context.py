from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncEngine

from finstats.client import ZenMoneyClient


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
    if not token.startswith("Bearer "):
        raise web.HTTPUnauthorized(reason="Invalid Authorization token")
    return token.removeprefix("Bearer ").strip()
