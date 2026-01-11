from __future__ import annotations

import asyncio
import signal

from aiohttp import web

from finstats.client import ZenMoneyClient
from finstats.http.health import HealthController
from finstats.http.middleware import access_log_middleware, auth_mw, request_id_middleware
from finstats.http.transactions import TransactionsController
from finstats.store.base import create_engine


def configure_stop_event() -> asyncio.Event:
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _stop() -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            pass

    return stop_event


async def serve_http(host: str = "0.0.0.0", port: int = 8080) -> None:
    app = create_app()

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    print(f"serving at http://{host}:{port}")
    stop_event = configure_stop_event()

    try:
        await stop_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()


def create_app() -> web.Application:
    app = web.Application(middlewares=[request_id_middleware, access_log_middleware])
    app.router.add_view("/health", HealthController)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.on_cleanup.append(on_cleanup)

    # main api (under auth)
    auth = web.Application(middlewares=[auth_mw])
    auth.router.add_view("/transactions", TransactionsController)

    app.add_subapp("/api/v1", auth)
    return app


async def on_startup(app: web.Application) -> None:
    app["engine"] = create_engine()
    client = ZenMoneyClient()
    client.create_session()
    app["client"] = client


async def on_shutdown(app: web.Application) -> None:
    pass


async def on_cleanup(app: web.Application) -> None:
    engine = app["engine"]
    if engine is not None:
        await engine.dispose()

    client = app["client"]
    if client is not None:
        await client.dispose()
