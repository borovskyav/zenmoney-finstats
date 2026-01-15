import datetime

import sqlalchemy as sa

from finstats.store.base import TimestampTable
from finstats.store.connection import ConnectionScope


class TimestampRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def get_last_timestamp(self) -> int:
        stmt = sa.select(TimestampTable.last_synced_timestamp).where(TimestampTable.id == 1)
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            ts = result.scalar_one()
            return int(ts.timestamp())

    async def save_last_timestamp(self, timestamp: int) -> None:
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
        stmt = sa.update(TimestampTable).where(TimestampTable.id == 1).values(last_synced_timestamp=dt)
        async with self.__connection_scope.acquire() as connection:
            await connection.execute(stmt)
