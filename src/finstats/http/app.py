from __future__ import annotations

import asyncio
import signal
from collections.abc import AsyncIterator

from aiohttp import web

from finstats.client import ZenMoneyClient
from finstats.container import Container, set_container
from finstats.http.accounts import AccountsController
from finstats.http.health import HealthController
from finstats.http.instruments import InstrumentsController
from finstats.http.middleware import auth_mw, error_middleware, request_id_middleware
from finstats.http.openapi import setup_openapi
from finstats.http.tags import TagsController
from finstats.http.transactions import TransactionsController
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
from finstats.store.base import create_engine
from finstats.store.connection import ConnectionScope


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
    app = web.Application(middlewares=[error_middleware, request_id_middleware])
    app.router.add_view("/health", HealthController)

    app.on_shutdown.append(on_shutdown)
    app.cleanup_ctx.append(app_context)

    # main api (under auth)
    auth = web.Application(middlewares=[auth_mw])
    auth.router.add_view("/transactions", TransactionsController)
    auth.router.add_view("/accounts", AccountsController)
    auth.router.add_view("/tags", TagsController)
    auth.router.add_view("/instruments", InstrumentsController)

    app.add_subapp("/api/v1", auth)

    setup_openapi(app)

    return app


async def app_context(app: web.Application) -> AsyncIterator[None]:
    container = Container()
    engine = create_engine()
    container.register(ConnectionScope, instance=ConnectionScope(engine))
    container.register(AccountsRepository)
    container.register(CompaniesRepository)
    container.register(CountriesRepository)
    container.register(InstrumentsRepository)
    container.register(MerchantsRepository)
    container.register(TagsRepository)
    container.register(TimestampRepository)
    container.register(TransactionsRepository)
    container.register(UsersRepository)

    client = ZenMoneyClient()
    client.create_session()
    container.register(ZenMoneyClient, instance=client)

    set_container(app, container)

    yield

    await engine.dispose()
    await client.dispose()


async def on_shutdown(app: web.Application) -> None:
    pass
