import datetime
from collections.abc import Iterable
from typing import Any

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import ZmDiffResponse, ZmTransaction
from finstats.store.base import TimestampTable, TransactionsTable


async def get_last_timestamp(connection: sa_async.AsyncConnection) -> int:
    stmt = sa.select(TimestampTable.last_synced_timestamp).where(TimestampTable.id == 1)
    result = await connection.execute(stmt)
    ts = result.scalar_one()
    return int(ts.timestamp())


async def save_diff(connection: sa_async.AsyncConnection, diff: ZmDiffResponse) -> None:
    await save_last_timestamp(connection, diff.server_timestamp)
    await save_transactions(connection, diff.transaction)


async def save_last_timestamp(connection: sa_async.AsyncConnection, timestamp: int) -> None:
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
    stmt = sa.update(TimestampTable).where(TimestampTable.id == 1).values(last_synced_timestamp=dt)
    await connection.execute(stmt)


async def save_transactions(connection: sa_async.AsyncConnection, transactions: list[ZmTransaction]) -> None:
    if not transactions or len(transactions):
        return

    stmt = sa_postgresql.insert(TransactionsTable).values(map_zm_transactions_to_rows(transactions))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in TransactionsTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[TransactionsTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


def map_zm_transactions_to_rows(txns: Iterable[ZmTransaction]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for t in txns:
        rows.append(
            {
                "id": t.id,
                "user": t.user,
                "income": t.income,
                "outcome": t.outcome,
                "changed": t.changed,
                "income_instrument": t.income_instrument,
                "outcome_instrument": t.outcome_instrument,
                "created": t.created,
                "original_payee": t.original_payee,
                "deleted": t.deleted,
                "viewed": t.viewed,
                "hold": t.hold,
                "qr_code": t.qr_code,
                "source": t.source,
                "income_account": t.income_account,
                "outcome_account": t.outcome_account,
                "comment": t.comment,
                "payee": t.payee,
                "op_income": t.op_income,
                "op_outcome": t.op_outcome,
                "op_income_instrument": t.op_income_instrument,
                "op_outcome_instrument": t.op_outcome_instrument,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "merchant": t.merchant,
                "income_bank_id": t.income_bank_id,
                "outcome_bank_id": t.outcome_bank_id,
                "reminder_marker": t.reminder_marker,
                "tags": t.tag or [],
                "date": t.date,
            }
        )
    return rows
