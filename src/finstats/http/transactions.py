from __future__ import annotations

from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncEngine

from finstats.contracts import DiffClient
from finstats.http.context import get_client, get_engine, get_token
from finstats.store.psql_store import get_last_timestamp, save_diff


class TransactionsController(web.View):
    async def get(self) -> web.Response:
        engine = get_engine(self.request)
        client = get_client(self.request)
        token = get_token(self.request)
        await sync_once(token, client, engine)
        return web.json_response({"api": "ok"})


async def sync_once(token: str, client: DiffClient, engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        timestamp = await get_last_timestamp(conn)
        diff = await client.fetch_diff(token, timestamp)
        await save_diff(conn, diff)
