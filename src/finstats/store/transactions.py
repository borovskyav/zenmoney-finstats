import datetime

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import (
    AccountId,
    TagId,
    ZmTransaction,
)
from finstats.store.base import (
    TransactionsTable,
)
from finstats.store.misc import from_dataclasses, to_dataclasses


async def get_transactions(
    connection: sa_async.AsyncConnection,
    offset: int = 0,
    limit: int = 100,
    from_date: datetime.date | None = None,  # from 1970 if none
    to_date: datetime.date | None = None,  # to now_date if none
    not_viewed: bool = False,
    account_id: AccountId | None = None,
    tags: list[TagId] | None = None,
) -> tuple[list[ZmTransaction], int]:
    if from_date is not None and to_date is not None and from_date > to_date:
        raise ValueError(f"from_date {from_date} > to_date {to_date}")

    where_clause = TransactionsTable.deleted.is_(False)
    if from_date:
        where_clause &= TransactionsTable.date >= from_date

    if to_date:
        where_clause &= TransactionsTable.date <= to_date

    if not_viewed:
        where_clause &= TransactionsTable.viewed.is_(False)

    if account_id:
        where_clause &= (TransactionsTable.income_account == account_id) | (TransactionsTable.outcome_account == account_id)

    if tags:
        where_clause &= TransactionsTable.tags.op("&&")(tags)

    stmt_count = sa.select(sa.func.count()).select_from(TransactionsTable).where(where_clause)
    total = (await connection.execute(stmt_count)).scalar_one()

    stmt = (
        sa.select(TransactionsTable)
        .order_by(TransactionsTable.date.desc(), TransactionsTable.created.desc(), TransactionsTable.id.desc())
        .offset(offset)
        .limit(limit)
        .where(where_clause)
    )

    result = await connection.execute(stmt)
    rows = result.all()
    return to_dataclasses(ZmTransaction, rows), total


async def save_transactions(connection: sa_async.AsyncConnection, transactions: list[ZmTransaction]) -> None:
    if not transactions:
        return

    stmt = sa_postgresql.insert(TransactionsTable).values(from_dataclasses(transactions))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in TransactionsTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[TransactionsTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)
