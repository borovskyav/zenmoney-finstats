import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import (
    InstrumentId,
    ZmInstrument,
)
from finstats.store.base import (
    InstrumentTable,
)
from finstats.store.misc import from_dataclasses, to_dataclasses


async def save_instruments(connection: sa_async.AsyncConnection, instruments: list[ZmInstrument]) -> None:
    if not instruments:
        return

    stmt = sa_postgresql.insert(InstrumentTable).values(from_dataclasses(instruments))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in InstrumentTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[InstrumentTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def get_instruments(connection: sa_async.AsyncConnection) -> list[ZmInstrument]:
    stmt = sa.select(InstrumentTable)
    result = await connection.execute(stmt)
    rows = result.all()
    return to_dataclasses(ZmInstrument, rows)


async def get_instruments_by_id(connection: sa_async.AsyncConnection, instrument_ids: list[InstrumentId]) -> list[ZmInstrument]:
    if not instrument_ids:
        return []
    stmt = sa.select(InstrumentTable).where(InstrumentTable.id.in_(instrument_ids))
    result = await connection.execute(stmt)
    rows = result.all()
    return to_dataclasses(ZmInstrument, rows)
