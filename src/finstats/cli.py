from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiohttp import web

from finstats.app import create_app
from finstats.args import CliArgs
from finstats.cli_syncer import CliSyncer
from finstats.container import get_container
from finstats.contracts import CliException, ZenMoneyClientException
from finstats.http.app import serve_http
from finstats.store.base import run_migrations


def main() -> None:
    try:
        run()
    except ZenMoneyClientException as e:
        print(f"ZenMoney client error: {str(e)}")
        sys.exit(3)
    except CliException as e:
        print(f"Cli error: {str(e)}")
        sys.exit(2)


def run() -> None:
    args = CliArgs()
    if args.is_version():
        print("0.1.0")
        return

    if args.is_migrate():
        run_migrations()
        return

    app = create_app()

    if args.is_serve():
        serve_http(app)
        return

    asyncio.run(run_command_in_context(app, args))


async def run_command_in_context(app: web.Application, args: CliArgs) -> None:
    async with command_context(app) as app:
        await run_command(app, args)


async def run_command(app: web.Application, args: CliArgs) -> None:
    cli_syncer = get_container(app).resolve(CliSyncer)
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


@asynccontextmanager
async def command_context(app: web.Application) -> AsyncIterator[web.Application]:
    runner = web.AppRunner(app)
    await runner.setup()
    try:
        yield app
    finally:
        await runner.cleanup()
