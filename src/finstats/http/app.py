from __future__ import annotations

import asyncio
import signal

from aiohttp import web

from finstats.client import ZenMoneyClient
from finstats.http.accounts import AccountsController
from finstats.http.health import HealthController
from finstats.http.instruments import InstrumentsController
from finstats.http.middleware import auth_mw, error_middleware, request_id_middleware
from finstats.http.openapi import setup_openapi
from finstats.http.tags import TagsController
from finstats.http.transactions import TransactionsController
from finstats.store.accounts import AccountsRepository
from finstats.store.base import create_engine
from finstats.store.companies import CompaniesRepository
from finstats.store.connection import ConnectionScope
from finstats.store.countries import CountriesRepository
from finstats.store.instruments import InstrumentsRepository
from finstats.store.merchants import MerchantsRepository
from finstats.store.tags import TagsRepository
from finstats.store.timestamp import TimestampRepository
from finstats.store.transactions import TransactionsRepository
from finstats.store.users import UsersRepository


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

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.on_cleanup.append(on_cleanup)

    # main api (under auth)
    auth = web.Application(middlewares=[auth_mw])
    auth.router.add_view("/transactions", TransactionsController)
    auth.router.add_view("/accounts", AccountsController)
    auth.router.add_view("/tags", TagsController)
    auth.router.add_view("/instruments", InstrumentsController)

    app.add_subapp("/api/v1", auth)

    # Setup OpenAPI 3.1.0 documentation
    setup_openapi(app)

    return app


async def on_startup(app: web.Application) -> None:
    engine = create_engine()
    connection_scope = ConnectionScope(engine)
    app["connection_scope"] = connection_scope
    app["accounts_repository"] = AccountsRepository(connection_scope)
    app["companies_repository"] = CompaniesRepository(connection_scope)
    app["countries_repository"] = CountriesRepository(connection_scope)
    app["instruments_repository"] = InstrumentsRepository(connection_scope)
    app["merchants_repository"] = MerchantsRepository(connection_scope)
    app["tags_repository"] = TagsRepository(connection_scope)
    app["timestamp_repository"] = TimestampRepository(connection_scope)
    app["transactions_repository"] = TransactionsRepository(connection_scope)
    app["users_repository"] = UsersRepository(connection_scope)

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
