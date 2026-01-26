import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.domain import Country, CountryId
from finstats.store.base import CountryTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses, to_dataclasses


class CountriesRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def save_countries(self, countries: list[Country]) -> None:
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

    async def get_country(self, country_id: CountryId) -> Country | None:
        countries = await self.get_countries_by_id([country_id])
        if len(countries) == 0:
            return None
        return countries[0]

    async def get_countries_by_id(self, country_ids: list[CountryId]) -> list[Country]:
        if not country_ids:
            return []
        stmt = sa.select(CountryTable).where(CountryTable.id.in_(country_ids))
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(Country, result.all())
