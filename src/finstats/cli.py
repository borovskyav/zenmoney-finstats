from __future__ import annotations

import logging
import sys

from finstats.app import MyApplication
from finstats.args import CliArgs
from finstats.container import Container
from finstats.models import CliException
from finstats.store import get_pg_url_from_env, run_migrations
from finstats.zenmoney import ZenMoneyClientException


def main() -> None:
    # time is writing direcly in fly.io logging system
    logging.basicConfig(level="INFO", stream=sys.stdout, format="%(levelname)s %(name)s %(message)s")

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
        run_migrations(get_pg_url_from_env(use_psycopg=True))
        return

    container = Container()

    new_app = MyApplication(container, args)
    new_app.initialize()
    new_app.run()
