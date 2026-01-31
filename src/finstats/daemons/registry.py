from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

import aio_background
from aio_background import Job
from aiohttp import web

from finstats.args import CliArgs
from finstats.container import Container
from finstats.daemons.base import BaseDaemon, CronDaemon, PeriodicDaemon


class DaemonRegistry:
    __slots__ = (
        "__container",
        "__daemons",
    )

    def __init__(self, container: Container) -> None:
        self.__daemons: dict[str, type[BaseDaemon]] = {}
        self.__container: Container = container

    def create_daemon_job(self, args: CliArgs) -> Callable[[web.Application], Coroutine[Any, Any, Job]]:
        name = args.get_daemon_name()
        daemon_type = self._get_daemon(name)

        async def create(app: web.Application) -> aio_background.Job:
            daemon = self.__container.resolve(daemon_type)
            if isinstance(daemon, CronDaemon):
                return aio_background.run_by_cron(
                    func=daemon.run,
                    cron_expr=daemon.get_cron_expr(),
                    name=name,
                )
            if isinstance(daemon, PeriodicDaemon):
                return aio_background.run_periodically(
                    func=daemon.run,
                    period=daemon.get_run_period_seconds(),
                    name=name,
                )
            raise ValueError(f"Unsupported daemon: {daemon}, daemon name: {name}")

        return create

    def register(self, name: str, daemon_cls: type[BaseDaemon]) -> None:
        if name in self.__daemons:
            raise ValueError(f"Daemon {name} already registered")
        self.__container.register(daemon_cls)
        self.__daemons[name] = daemon_cls

    def _get_daemon(self, name: str) -> type[BaseDaemon]:
        if name not in self.__daemons:
            raise ValueError(f"Daemon {name} not registered")
        return self.__daemons[name]
