from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.domain import ZmCountry
from finstats.store.base import CountryTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses


class CountriesRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def save_countries(self, countries: list[ZmCountry]) -> None:
        if not countries:
            return

        stmt = sa_postgresql.insert(CountryTable).values(from_dataclasses(countries))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in CountryTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[CountryTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)
