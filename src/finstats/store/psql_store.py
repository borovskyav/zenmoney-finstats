import datetime

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import (
    ZmCompany,
    ZmCountry,
    ZmDiffResponse,
    ZmInstrument,
    ZmMerchant,
    ZmUser,
)
from finstats.store.accounts import save_accounts
from finstats.store.base import (
    CompanyTable,
    CountryTable,
    InstrumentTable,
    MerchantTable,
    TimestampTable,
    UserTable,
)
from finstats.store.misc import from_dataclasses
from finstats.store.tags import save_tags
from finstats.store.transactions import save_transactions


async def get_last_timestamp(connection: sa_async.AsyncConnection) -> int:
    stmt = sa.select(TimestampTable.last_synced_timestamp).where(TimestampTable.id == 1)
    result = await connection.execute(stmt)
    ts = result.scalar_one()
    return int(ts.timestamp())


async def save_last_timestamp(connection: sa_async.AsyncConnection, timestamp: int) -> None:
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
    stmt = sa.update(TimestampTable).where(TimestampTable.id == 1).values(last_synced_timestamp=dt)
    await connection.execute(stmt)


async def save_diff(connection: sa_async.AsyncConnection, diff: ZmDiffResponse) -> None:
    await save_last_timestamp(connection, diff.server_timestamp)
    await save_accounts(connection, diff.account)
    await save_companies(connection, diff.company)
    await save_countries(connection, diff.country)
    await save_instruments(connection, diff.instrument)
    await save_merchants(connection, diff.merchant)
    await save_tags(connection, diff.tag)
    for transaction in diff.transaction:
        await save_transactions(connection, [transaction])
    await save_users(connection, diff.user)


async def save_companies(connection: sa_async.AsyncConnection, companies: list[ZmCompany]) -> None:
    if not companies:
        return

    stmt = sa_postgresql.insert(CompanyTable).values(from_dataclasses(companies))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in CompanyTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[CompanyTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_countries(connection: sa_async.AsyncConnection, countries: list[ZmCountry]) -> None:
    if not countries:
        return

    stmt = sa_postgresql.insert(CountryTable).values(from_dataclasses(countries))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in CountryTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[CountryTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


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


async def save_merchants(connection: sa_async.AsyncConnection, merchants: list[ZmMerchant]) -> None:
    if not merchants:
        return

    stmt = sa_postgresql.insert(MerchantTable).values(from_dataclasses(merchants))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in MerchantTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[MerchantTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


async def save_users(connection: sa_async.AsyncConnection, users: list[ZmUser]) -> None:
    if not users:
        return

    stmt = sa_postgresql.insert(UserTable).values(from_dataclasses(users))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in UserTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[UserTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)
