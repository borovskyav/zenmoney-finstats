from __future__ import annotations

from collections.abc import AsyncIterator

import aio_background
from aiohttp import web

from finstats.args import CliArgs
from finstats.client.client import ZenMoneyClient
from finstats.container import Container, get_container, set_container
from finstats.daemons import DaemonRegistry
from finstats.http.health import HealthController
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
from finstats.syncer import Syncer


def create_app(args: CliArgs) -> web.Application:
    app = web.Application()
    app.router.add_view("/health", HealthController)

    container = Container()
    container.register(CliArgs, instance=args)
    set_container(app, container)
    registry = DaemonRegistry(container)

    app.cleanup_ctx.append(app_context)
    if args.is_daemon():
        app.cleanup_ctx.append(aio_background.aiohttp_setup_ctx(registry.create_daemon_job(args), timeout=5.0))  # ty:ignore[possibly-missing-attribute]

    return app


async def app_context(app: web.Application) -> AsyncIterator[None]:
    container = get_container(app)
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
    container.register(Syncer)

    client = ZenMoneyClient()
    container.register(ZenMoneyClient, instance=client)

    yield

    await engine.dispose()
    await client.dispose()
