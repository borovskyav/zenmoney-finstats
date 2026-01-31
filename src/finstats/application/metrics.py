from __future__ import annotations

from aiohttp import web
from prometheus_client import generate_latest


class MetricsController(web.View):
    async def get(self) -> web.Response:
        return web.Response(body=generate_latest(), content_type="text/plain")
