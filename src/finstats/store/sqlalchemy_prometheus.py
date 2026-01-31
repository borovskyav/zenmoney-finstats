from __future__ import annotations

import time
from typing import TYPE_CHECKING, cast

from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import QueuePool

if TYPE_CHECKING:
    from collections.abc import Iterable

    from opentelemetry.metrics import Meter
    from sqlalchemy.engine import Connection
    from sqlalchemy.engine.interfaces import DBAPIConnection, DBAPICursor, ExecutionContext
    from sqlalchemy.pool import ConnectionPoolEntry, Pool

_query_buckets = [0.001, 0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
_meter = metrics.get_meter("sqlalchemy")

_query_duration = _meter.create_histogram(
    "db_client_query_duration",
    unit="s",
    description="Database query execution time",
    explicit_bucket_boundaries_advisory=_query_buckets,
)

_transactions = _meter.create_counter(
    "db_client_transactions",
    unit="1",
    description="Total database transactions",
)

_acquire_count = _meter.create_counter(
    "db_client_pool_acquire",
    unit="1",
    description="Cumulative count of successful acquires from the pool",
)

_connection_usage_duration = _meter.create_histogram(
    "db_client_pool_connection_usage_duration",
    unit="s",
    description="How long connections are held before returning to pool",
    explicit_bucket_boundaries_advisory=_query_buckets,
)

_new_conns_count = _meter.create_counter(
    "db_client_pool_new_connections",
    unit="1",
    description="Cumulative count of new connections created",
)

_closed_conns_count = _meter.create_counter(
    "db_client_pool_closed_connections",
    unit="1",
    description="Cumulative count of connections closed",
)


def _configure_pool_gauges_for_queue_pool(
    meter: Meter,
    pool: Pool,
    attrs: dict[str, str],
) -> None:
    required_methods = ("checkedout", "checkedin", "size", "overflow")
    if not all(callable(getattr(pool, m, None)) for m in required_methods):
        return

    queue_pool = cast(QueuePool, pool)

    def observe_acquired(options: CallbackOptions) -> Iterable[Observation]:
        return [Observation(queue_pool.checkedout(), attrs)]

    def observe_idle(options: CallbackOptions) -> Iterable[Observation]:
        return [Observation(queue_pool.checkedin(), attrs)]

    def observe_total(options: CallbackOptions) -> Iterable[Observation]:
        return [Observation(queue_pool.size(), attrs)]

    def observe_overflow(options: CallbackOptions) -> Iterable[Observation]:
        return [Observation(queue_pool.overflow(), attrs)]

    meter.create_observable_gauge(
        "db_client_pool_acquired_connections",
        callbacks=[observe_acquired],
        unit="1",
        description="Number of currently acquired connections",
    )
    meter.create_observable_gauge(
        "db_client_pool_idle_connections",
        callbacks=[observe_idle],
        unit="1",
        description="Number of currently idle connections",
    )
    meter.create_observable_gauge(
        "db_client_pool_total_connections",
        callbacks=[observe_total],
        unit="1",
        description="Total connections in the pool",
    )
    meter.create_observable_gauge(
        "db_client_pool_overflow_connections",
        callbacks=[observe_overflow],
        unit="1",
        description="Current overflow connections beyond pool size",
    )


def instrument_engine(engine: AsyncEngine, pool_name: str = "default") -> None:
    sync_engine = engine.sync_engine
    pool = sync_engine.pool
    attrs = {"pool_name": pool_name}

    _configure_pool_gauges_for_queue_pool(_meter, pool, attrs)

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
        _query_duration.record(time.perf_counter() - start, attrs)

    @event.listens_for(sync_engine, "commit")
    def on_commit(conn: Connection) -> None:
        _transactions.add(1, {**attrs, "status": "commit"})

    @event.listens_for(sync_engine, "rollback")
    def on_rollback(conn: Connection) -> None:
        _transactions.add(1, {**attrs, "status": "rollback"})

    @event.listens_for(sync_engine, "checkout")
    def on_checkout(
        dbapi_conn: DBAPIConnection,
        connection_record: ConnectionPoolEntry,
        connection_proxy: Connection,
    ) -> None:
        _acquire_count.add(1, attrs)
        connection_record.info["checkout_start"] = time.perf_counter()

    @event.listens_for(sync_engine, "checkin")
    def on_checkin(
        dbapi_conn: DBAPIConnection,
        connection_record: ConnectionPoolEntry,
    ) -> None:
        start: float | None = connection_record.info.pop("checkout_start", None)
        if start is not None:
            _connection_usage_duration.record(time.perf_counter() - start, attrs)

    @event.listens_for(pool, "connect")
    def on_connect(
        dbapi_conn: DBAPIConnection,
        connection_record: ConnectionPoolEntry,
    ) -> None:
        _new_conns_count.add(1, attrs)

    @event.listens_for(pool, "close")
    def on_close(
        dbapi_conn: DBAPIConnection,
        connection_record: ConnectionPoolEntry,
    ) -> None:
        _closed_conns_count.add(1, attrs)
