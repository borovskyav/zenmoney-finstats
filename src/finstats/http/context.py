from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncEngine

from finstats.client import ZenMoneyClient


def get_engine(request: web.Request) -> AsyncEngine:
    engine = request.app["engine"]
    if engine is None:
        raise web.HTTPInternalServerError(reason="No engine found")
    return engine


def get_client(request: web.Request) -> ZenMoneyClient:
    client = request.app["client"]
    if client is None:
        raise web.HTTPInternalServerError(reason="No client found")
    return client
