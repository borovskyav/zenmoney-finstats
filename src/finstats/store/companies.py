from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.domain import Company
from finstats.store.base import CompanyTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses


class CompaniesRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def save_companies(self, companies: list[Company]) -> None:
        if not companies:
            return

        stmt = sa_postgresql.insert(CompanyTable).values(from_dataclasses(companies))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in CompanyTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[CompanyTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)
