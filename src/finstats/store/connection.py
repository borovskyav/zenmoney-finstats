import asyncio
import contextlib
import contextvars
import sys
import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import AbstractAsyncContextManager
from types import TracebackType

import sqlalchemy.ext.asyncio as sa_async

connection_var = contextvars.ContextVar[sa_async.AsyncConnection | None](str(uuid.uuid4()), default=None)


class ShieldedConnectionContext(AbstractAsyncContextManager[sa_async.AsyncConnection]):
    __slots__ = ("__connection_ctx",)

    def __init__(self, connection_ctx: AbstractAsyncContextManager[sa_async.AsyncConnection]) -> None:
        self.__connection_ctx = connection_ctx

    async def __aenter__(self) -> sa_async.AsyncConnection:
        aenter_task = asyncio.create_task(self.__connection_ctx.__aenter__())
        try:
            return await asyncio.shield(aenter_task)
        except asyncio.CancelledError:
            await aenter_task
            await self.__connection_ctx.__aexit__(*sys.exc_info())
            raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await asyncio.shield(self.__connection_ctx.__aexit__(exc_type, exc, tb))


class ConnectionScope:
    __slots__ = ("__engine",)

    def __init__(self, engine: sa_async.AsyncEngine) -> None:
        self.__engine = engine

    @contextlib.asynccontextmanager
    async def acquire(self) -> AsyncIterator[sa_async.AsyncConnection]:
        context_connection = self.__get_context_connection()
        if context_connection is not None:
            yield context_connection
        else:
            async with self._acquire_connection_with_transaction(self.__engine) as connection:
                with self.__set_context_connection(connection):
                    yield connection

    def check_is_opened(self) -> None:
        context_connection = self.__get_context_connection()
        if context_connection is None:
            raise RuntimeError("ConnectionScope should be already opened")

    @staticmethod
    def _acquire_connection_with_transaction(
        engine: sa_async.AsyncEngine,
    ) -> AbstractAsyncContextManager[sa_async.AsyncConnection]:
        return ShieldedConnectionContext(engine.begin())

    @staticmethod
    def __get_context_connection() -> sa_async.AsyncConnection | None:
        return connection_var.get()

    @staticmethod
    @contextlib.contextmanager
    def __set_context_connection(connection: sa_async.AsyncConnection) -> Iterator[None]:
        token = connection_var.set(connection)
        try:
            yield
        finally:
            connection_var.reset(token)
