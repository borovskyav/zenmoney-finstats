import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import InstrumentId, ZmInstrument
from finstats.store.base import InstrumentTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses, to_dataclasses


class InstrumentsRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def get_instruments(self) -> list[ZmInstrument]:
        stmt = sa.select(InstrumentTable).order_by(InstrumentTable.id.asc())
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(ZmInstrument, result.all())

    async def get_instruments_by_id(self, instrument_ids: list[InstrumentId]) -> list[ZmInstrument]:
        if not instrument_ids:
            return []
        stmt = sa.select(InstrumentTable).where(InstrumentTable.id.in_(instrument_ids))
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(ZmInstrument, result.all())

    async def save_instruments(self, instruments: list[ZmInstrument]) -> None:
        if not instruments:
            return

        stmt = sa_postgresql.insert(InstrumentTable).values(from_dataclasses(instruments))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in InstrumentTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[InstrumentTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)
