from __future__ import annotations

from aiohttp import web

from finstats.http.context import get_engine
from finstats.store.psql_store import get_last_timestamp


class HealthController(web.View):
    async def get(self) -> web.Response:
        engine = get_engine(self.request)
        last_timestamp: str = "0"

        try:
            async with engine.connect() as connection:
                last_timestamp = f"{await get_last_timestamp(connection)}"
        except Exception:
            last_timestamp = "psql is not available"

        return web.json_response({"api": "ok", "last_synced_timestamp": f"{last_timestamp}"})
