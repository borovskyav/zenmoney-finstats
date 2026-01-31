from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import aio_background
from aiohttp import web

from finstats.application.health import HealthController
from finstats.application.metrics import MetricsController
from finstats.application.telemetry import configure_metrics
from finstats.args import CliArgs
from finstats.container import Container, get_container, set_container
from finstats.daemons import DaemonRegistry


class Application:
    __slots__ = (
        "__args",
        "__container",
        "__app",
    )

    @property
    def app(self) -> web.Application:
        return self.__app

    def __init__(self, container: Container, args: CliArgs) -> None:
        self.__app = web.Application()
        self.__args = args
        self.__container = container
        self.__container.register(CliArgs, instance=args)
        set_container(self.__app, self.__container)

    def initialize(self) -> web.Application:
        configure_metrics()
        self._register_service_routes(self.__app)

        registry = DaemonRegistry(self.__container)
        self._configure_daemons(registry)

        async def app_ctx(app: web.Application) -> AsyncIterator[None]:
            async with self._configure_context(container=get_container(app)):
                yield

        self.__app.cleanup_ctx.append(app_ctx)

        if self.__args.is_daemon():
            self.__app.cleanup_ctx.append(
                aio_background.aiohttp_setup_ctx(  # ty:ignore[possibly-missing-attribute]
                    registry.create_daemon_job(self.__args),
                    timeout=5.0,
                ),
            )

        if self.__args.is_serve():
            self._configure_http_server(self.__app, self.__args)

        return self.__app

    def run(self) -> None:
        if self.__args.is_serve() or self.__args.is_daemon():
            web.run_app(self.__app, host="0.0.0.0", port=self.__args.get_port())
            return

        asyncio.run(self.__run_command_in_context())

    def _register_service_routes(self, app: web.Application) -> None:
        app.router.add_view("/health", HealthController)
        app.router.add_view("/metrics", MetricsController)

    def _configure_daemons(self, registry: DaemonRegistry) -> None:
        pass

    def _configure_http_server(self, app: web.Application, args: CliArgs) -> None:
        pass

    @asynccontextmanager
    async def _configure_context(self, container: Container) -> AsyncIterator[None]:
        yield

    async def _run_command(self, app: web.Application, args: CliArgs) -> None:
        pass

    async def __run_command_in_context(self) -> None:
        async with self.__command_context():
            await self._run_command(self.__app, self.__args)

    @asynccontextmanager
    async def __command_context(self) -> AsyncIterator[None]:
        runner = web.AppRunner(self.__app)
        await runner.setup()
        try:
            yield
        finally:
            await runner.cleanup()
