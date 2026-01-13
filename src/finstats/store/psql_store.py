import dataclasses
import datetime
from collections.abc import Sequence
from typing import Any, get_origin

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import (
    ZmAccount,
    ZmCompany,
    ZmCountry,
    ZmDiffResponse,
    ZmInstrument,
    ZmMerchant,
    ZmTag,
    ZmTransaction,
    ZmUser,
)
from finstats.store.base import (
    AccountTable,
    CompanyTable,
    CountryTable,
    InstrumentTable,
    MerchantTable,
    TagTable,
    TimestampTable,
    TransactionsTable,
    UserTable,
)


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


async def save_accounts(connection: sa_async.AsyncConnection, accounts: list[ZmAccount]) -> None:
    if not accounts:
        return

    stmt = sa_postgresql.insert(AccountTable).values(from_dataclasses(accounts))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in AccountTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[AccountTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


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


async def save_tags(connection: sa_async.AsyncConnection, tags: list[ZmTag]) -> None:
    if not tags:
        return

    stmt = sa_postgresql.insert(TagTable).values(from_dataclasses(tags))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in TagTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[TagTable.id],
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


async def get_transactions(
    connection: sa_async.AsyncConnection,
    offset: int = 0,
    limit: int = 100,
    from_date: datetime.date | None = None,  # from 1970 if none
    to_date: datetime.date | None = None,  # to now_date if none
) -> tuple[list[ZmTransaction], int]:
    if from_date is not None and to_date is not None and from_date > to_date:
        raise ValueError(f"from_date {from_date} > to_date {to_date}")

    where_clause = TransactionsTable.deleted.is_(False)
    if from_date:
        where_clause &= TransactionsTable.date >= from_date

    if to_date:
        where_clause &= TransactionsTable.date <= to_date

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
    if not transactions or len(transactions) == 0:
        return

    stmt = sa_postgresql.insert(TransactionsTable).values(from_dataclasses(transactions))

    excluded = stmt.excluded
    set_cols = {c.name: getattr(excluded, c.name) for c in TransactionsTable.__table__.columns if c.name != "id"}

    stmt = stmt.on_conflict_do_update(
        index_elements=[TransactionsTable.id],
        set_=set_cols,
    )
    await connection.execute(stmt)


__field_names: dict[type, tuple[str, ...]] = {}


def from_dataclass[T](cls: T) -> dict[str, Any]:
    if not dataclasses.is_dataclass(cls) or isinstance(cls, type):
        raise TypeError("content must be a dataclass instance")

    return dataclasses.asdict(cls)


def from_dataclasses[T](cls: Sequence[T]) -> Sequence[dict[str, Any]]:
    return [from_dataclass(c) for c in cls]


def to_dataclass[T](cls: type[T], row: sa.Row) -> T:
    field_names = __field_names.get(cls)
    if not field_names:
        effective_cls = get_origin(cls) or cls
        field_names = tuple(field.name for field in dataclasses.fields(effective_cls))
        __field_names[cls] = field_names

    return cls(**{field_name: getattr(row, field_name) for field_name in field_names})


def to_dataclasses[T](cls: type[T], rows: Sequence[sa.Row]) -> list[T]:
    return [to_dataclass(cls, row) for row in rows]
