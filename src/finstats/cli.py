from __future__ import annotations

import asyncio
import sys

from finstats.args import CliArgs
from finstats.cli_syncer import CliSyncer
from finstats.client import ZenMoneyClient, ZenMoneyClientException
from finstats.contracts import CliException, NullStore, NullSyncer, Syncer


def main() -> None:
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

    token = args.get_token()
    store = NullStore()

    async with ZenMoneyClient(token) as client:
        syncer = CliSyncer(client, store) if args.is_cli() else NullSyncer()
        if args.is_dry_run():
            await dry_run(syncer, args)
            return
        if args.is_sync():
            await syncer.sync_once()
            return


async def dry_run(syncer: Syncer, args: CliArgs) -> None:
    timestamp = args.get_timestamp()
    out = args.get_output_file()
    print(f"dry run, run from {timestamp} out: {out}")

    await syncer.dry_run(timestamp, out)
