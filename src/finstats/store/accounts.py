import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import AccountId, ZmAccount
from finstats.store.base import AccountTable
from finstats.store.misc import from_dataclasses, to_dataclass, to_dataclasses


async def get_account(connection: sa_async.AsyncConnection, account_id: AccountId) -> ZmAccount | None:
    stmt = sa.select(AccountTable).where(AccountTable.id == account_id)
    result = await connection.execute(stmt)
    row = result.one_or_none()
    if not row:
        return None
    return to_dataclass(ZmAccount, row)


async def get_accounts(
    connection: sa_async.AsyncConnection,
    archive: bool = False,
    show_debts: bool = False,
) -> list[ZmAccount]:
    stmt = sa.select(AccountTable)

    if archive:
        stmt = stmt.where(AccountTable.archive.is_(archive))

    if not show_debts:
        stmt = stmt.where(AccountTable.type != "debt")

    result = await connection.execute(stmt)
    rows = result.all()
    return to_dataclasses(ZmAccount, rows)


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
