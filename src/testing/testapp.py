from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from finstats.app import MyApplication
from finstats.args import CliArgs
from finstats.container import Container


class WebArgs(CliArgs):
    def __init__(self) -> None:
        super().__init__([])

    def is_serve(self) -> bool:
        return True


class TestApplication(MyApplication):
    def __init__(self, container: Container) -> None:
        super().__init__(container, WebArgs())

    @asynccontextmanager
    async def _configure_context(self, container: Container) -> AsyncIterator[None]:
        yield
