from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator

from aiohttp import web

from finstats.cli_syncer import CliSyncer
from finstats.client import ZenMoneyClient
from finstats.container import Container, set_container
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


def create_app() -> web.Application:
    logging.basicConfig(
        level="INFO",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    app = web.Application()
    app.router.add_view("/health", HealthController)

    app.cleanup_ctx.append(app_context)
    app.on_shutdown.append(on_shutdown)

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
    container.register(CliSyncer)

    client = ZenMoneyClient()
    client.create_session()
    container.register(ZenMoneyClient, instance=client)

    set_container(app, container)

    yield

    await engine.dispose()
    await client.dispose()


async def on_shutdown(app: web.Application) -> None:
    pass
