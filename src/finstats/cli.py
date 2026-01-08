from __future__ import annotations

import argparse
import asyncio
import os
import sys

from finstats.client import ZenMoneyClient, ZenMoneyClientException
from finstats.file import parse_and_validate_path, write_content_to_file

ZENTOKEN = "ZENTOKEN"


class CliException(Exception):
    pass


def main() -> None:
    try:
        asyncio.run(run())
    except ZenMoneyClientException as e:
        print(f"ZenMoney client error: {str(e)}")
        sys.exit(3)
    except CliException as e:
        print(f"Cli error: {str(e)}")
        sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="finstats")
    p.add_argument("--version", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--timestamp", default=None, type=int)
    p.add_argument("--out", default="data.json")
    return p


def get_zentoken_from_env() -> str:
    return os.getenv(ZENTOKEN, "")


async def run() -> None:
    args = build_parser().parse_args()
    if args.version:
        print("0.1.0")
        return

    token = get_zentoken_from_env()
    if token == "":
        raise CliException("ZENTOKEN env is not specified")
    print(f"token: {token}")

    async with ZenMoneyClient(token) as client:
        if args.dry_run:
            await dry_run(client, args)


async def dry_run(client: ZenMoneyClient, args: argparse.Namespace) -> None:
    timestamp = args.timestamp
    if timestamp is None:
        raise CliException("timestamp not specified")

    out = args.out

    path = parse_and_validate_path(out)

    print(f"dry run, run from {timestamp} out: {path}")

    response = await client.fetch_diff(timestamp)
    print(response.server_timestamp)
    print(len(response.transaction))

    write_content_to_file(path, response)
