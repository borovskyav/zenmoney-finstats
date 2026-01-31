from __future__ import annotations

import time
from typing import TYPE_CHECKING

from opentelemetry import metrics
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from sqlalchemy.engine.interfaces import DBAPICursor, ExecutionContext


_meter = metrics.get_meter("sqlalchemy")

_query_duration = _meter.create_histogram(
    "db_client_query_duration",
    unit="s",
    description="Database query execution time",
)

_transactions = _meter.create_counter(
    "db_client_transactions",
    unit="1",
    description="Total database transactions",
)


def instrument_engine(
    engine: AsyncEngine,
    pool_name: str = "default",
    slow_query_threshold: float = 0.5,
) -> None:
    sync_engine = engine.sync_engine

    @event.listens_for(sync_engine, "before_cursor_execute")
    def before_execute(
        conn: Connection,
        cursor: DBAPICursor,
        statement: str,
        parameters: tuple[object, ...] | dict[str, object] | None,
        context: ExecutionContext | None,
        executemany: bool,
    ) -> None:
        conn.info["query_start"] = time.perf_counter()

    @event.listens_for(sync_engine, "after_cursor_execute")
    def after_execute(
        conn: Connection,
        cursor: DBAPICursor,
        statement: str,
        parameters: tuple[object, ...] | dict[str, object] | None,
        context: ExecutionContext | None,
        executemany: bool,
    ) -> None:
        start: float | None = conn.info.pop("query_start", None)
        if start is None:
            return

        duration = time.perf_counter() - start
        _query_duration.record(duration, {"pool_name": pool_name})

    @event.listens_for(sync_engine, "commit")
    def on_commit(conn: Connection) -> None:
        _transactions.add(1, {"pool_name": pool_name, "status": "commit"})

    @event.listens_for(sync_engine, "rollback")
    def on_rollback(conn: Connection) -> None:
        _transactions.add(1, {"pool_name": pool_name, "status": "rollback"})
