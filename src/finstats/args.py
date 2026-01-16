import argparse
import os

from finstats.contracts import CliException

ZENTOKEN = "ZENTOKEN"


class CliArgs:
    def __init__(self) -> None:
        p = argparse.ArgumentParser(prog="finstats")

        p.add_argument("--version", action="store_true")
        p.add_argument("--migrate", action="store_true")

        p.add_argument("--daemon", default=None, type=str)
        p.add_argument("--serve", action="store_true")

        # dry-run command + token + timestamp + out (data.json by default)
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--token", default=None, type=str)
        p.add_argument("--timestamp", default=None, type=int)
        p.add_argument("--out", default="data.json", type=str)

        # sync command + token
        p.add_argument("--sync", action="store_true")

        self.__args = p.parse_args()

    def is_version(self) -> bool:
        return self.__args.version

    def is_migrate(self) -> bool:
        return self.__args.migrate

    def is_daemon(self) -> bool:
        return self.__args.daemon is not None

    def is_serve(self) -> bool:
        return self.__args.serve

    def is_dry_run(self) -> bool:
        return self.__args.dry_run

    def get_timestamp(self) -> int:
        timestamp = self.__args.timestamp
        if timestamp is None:
            raise CliException("timestamp not specified")
        return timestamp

    def get_token(self) -> str:
        token = self.__args.token
        if token is not None:
            return token
        token = os.getenv(ZENTOKEN)
        if token is not None:
            return token
        raise CliException("ZENTOKEN env or --token is not specified")

    def get_output_file(self) -> str:
        return self.__args.out

    def is_sync(self) -> bool:
        return self.__args.sync
