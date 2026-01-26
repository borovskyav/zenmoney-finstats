import abc
import argparse
import os

from finstats.models import CliException


class HostingEnvironment(abc.ABC):
    @abc.abstractmethod
    def server(self) -> str: ...

    @abc.abstractmethod
    def version(self) -> str: ...


class LocalEnvironment(HostingEnvironment):
    def __init__(self, args: CliArgs) -> None:
        self._args = args

    def version(self) -> str:
        return "v1"

    def server(self) -> str:
        return f"http://localhost:{self._args.get_port()}"


class FlyEnvironment(HostingEnvironment):
    def __init__(self, local: LocalEnvironment) -> None:
        self._local = local

    def version(self) -> str:
        # FLY_IMAGE_REF=registry.fly.io/finstats:main-9219a32
        image_ref = os.getenv("FLY_IMAGE_REF")
        if image_ref is None or ":" not in image_ref:
            return self._local.version()
        return image_ref.rsplit(":", 1)[-1]

    def server(self) -> str:
        app_name = os.getenv("FLY_APP_NAME")
        if app_name is None:
            return self._local.server()
        return f"https://{app_name}.fly.dev"


class CliArgs:
    __slots__ = (
        "__args",
        "__environment",
    )

    def __init__(self, argv: list[str] | None = None) -> None:
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

        local_environment = LocalEnvironment(self)
        self.__environment: HostingEnvironment = FlyEnvironment(local_environment) if (os.getenv("FLY_MACHINE_ID") is not None) else local_environment
        self.__args = p.parse_args(argv)

    def is_version(self) -> bool:
        return self.__args.version

    def is_migrate(self) -> bool:
        return self.__args.migrate

    def is_daemon(self) -> bool:
        return self.__args.daemon is not None

    def get_daemon_name(self) -> str:
        daemon = self.__args.daemon
        if daemon is None:
            raise CliException("daemon not specified")
        return daemon

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
        token = os.getenv("ZENTOKEN")
        if token is not None:
            return token
        raise CliException("ZENTOKEN env or --token is not specified")

    def get_port(self) -> int:
        port = os.getenv("APP_PORT")
        return 8080 if port is None else int(port)

    def get_output_file(self) -> str:
        return self.__args.out

    def is_sync(self) -> bool:
        return self.__args.sync

    @property
    def hosting_environment(self) -> HostingEnvironment:
        return self.__environment
