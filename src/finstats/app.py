from __future__ import annotations

from collections.abc import AsyncIterator

import aio_background
from aiohttp import web

from finstats.args import CliArgs
from finstats.container import Container, get_container, set_container
from finstats.daemons import DaemonRegistry
from finstats.server import HealthController
from finstats.store import configure_container, get_pg_url_from_env
from finstats.syncer import Syncer
from finstats.zenmoney import ZenMoneyClient


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

    pg_url = get_pg_url_from_env()
    engine = configure_container(container, pg_url)
    container.register(Syncer)

    client = ZenMoneyClient()
    container.register(ZenMoneyClient, instance=client)

    yield

    await engine.dispose()
    await client.dispose()
