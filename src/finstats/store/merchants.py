import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import MerchantId, ZmMerchant
from finstats.store.base import MerchantTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses, to_dataclasses


class MerchantsRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def get_merchants(self) -> list[ZmMerchant]:
        stmt = sa.select(MerchantTable)
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(ZmMerchant, result.all())

    async def get_merchants_by_id(self, merchant_ids: list[MerchantId]) -> list[ZmMerchant]:
        if not merchant_ids:
            return []
        stmt = sa.select(MerchantTable).where(MerchantTable.id.in_(merchant_ids))
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(ZmMerchant, result.all())

    async def save_merchants(self, merchants: list[ZmMerchant]) -> None:
        if not merchants:
            return

        stmt = sa_postgresql.insert(MerchantTable).values(from_dataclasses(merchants))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in MerchantTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[MerchantTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)
