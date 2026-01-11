from __future__ import annotations

import asyncio
import logging
import sys

from finstats.args import CliArgs
from finstats.cli_syncer import CliSyncer
from finstats.contracts import CliException, ZenMoneyClientException
from finstats.http.app import serve_http
from finstats.store.base import run_migrations


def main() -> None:
    logging.basicConfig(
        level="INFO",
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    try:
        asyncio.run(run())
    except ZenMoneyClientException as e:
        print(f"ZenMoney client error: {str(e)}")
        sys.exit(3)
    except CliException as e:
        print(f"Cli error: {str(e)}")
        sys.exit(2)


async def run() -> None:
    args = CliArgs()
    if args.is_version():
        print("0.1.0")
        return

    if args.is_migrate():
        run_migrations()
        return

    if args.is_run():
        await serve_http()
        return

    token = args.get_token()
    async with CliSyncer(token) as syncer:
        if args.is_dry_run():
            await dry_run(syncer, args)
            return
        if args.is_sync():
            await syncer.sync_once()
            return


async def dry_run(syncer: CliSyncer, args: CliArgs) -> None:
    timestamp = args.get_timestamp()
    out = args.get_output_file()
    print(f"dry run, run from {timestamp} out: {out}")

    await syncer.dry_run(timestamp, out)
