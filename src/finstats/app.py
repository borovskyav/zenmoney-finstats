from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiohttp import web

from finstats.application import Application
from finstats.args import CliArgs
from finstats.container import Container, get_container
from finstats.daemons import DaemonRegistry, SyncDiffDaemon
from finstats.server import create_web_server, register_service_routes
from finstats.store import configure_container, get_pg_url_from_env
from finstats.syncer import Syncer
from finstats.zenmoney import ZenMoneyClient


class MyApplication(Application):
    def _register_service_routes(self, app: web.Application) -> None:
        register_service_routes(app)

    def _configure_daemons(self, registry: DaemonRegistry) -> None:
        registry.register("sync", SyncDiffDaemon)

    @asynccontextmanager
    async def _configure_context(self, container: Container) -> AsyncIterator[None]:
        async with super()._configure_context(container):
            pg_url = get_pg_url_from_env()
            engine = configure_container(container, pg_url)
            container.register(Syncer)

            client = ZenMoneyClient()
            container.register(ZenMoneyClient, instance=client)

            yield

            await engine.dispose()
            await client.dispose()

    def _configure_http_server(self, app: web.Application, args: CliArgs) -> None:
        create_web_server(app, args)

    async def _run_command(self, app: web.Application, args: CliArgs) -> None:
        cli_syncer = get_container(app).resolve(Syncer)
        token = args.get_token()

        if args.is_dry_run():
            timestamp = args.get_timestamp()
            out = args.get_output_file()
            print(f"dry run, run from {timestamp} out: {out}")

            await cli_syncer.dry_run(token, timestamp, out)
            return
        if args.is_sync():
            await cli_syncer.sync_once(token)
            return
