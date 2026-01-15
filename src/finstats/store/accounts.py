import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import AccountId, ZmAccount
from finstats.store.base import AccountTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses, to_dataclass, to_dataclasses


class AccountsRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def get_account(self, account_id: AccountId) -> ZmAccount | None:
        stmt = sa.select(AccountTable).where(AccountTable.id == account_id)
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclass(ZmAccount, result.one_or_none())

    async def get_accounts(self, show_archive: bool = False, show_debts: bool = False) -> list[ZmAccount]:
        stmt = sa.select(AccountTable).where(AccountTable.archive.is_(show_archive))
        if not show_debts:
            stmt = stmt.where(AccountTable.type != "debt")
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(ZmAccount, result.all())

    async def get_accounts_by_id(self, account_ids: list[AccountId]) -> list[ZmAccount]:
        if not account_ids:
            return []
        stmt = sa.select(AccountTable).where(AccountTable.id.in_(account_ids))
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(ZmAccount, result.all())

    async def save_accounts(self, accounts: list[ZmAccount]) -> None:
        if not accounts:
            return

        stmt = sa_postgresql.insert(AccountTable).values(from_dataclasses(accounts))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in AccountTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[AccountTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)
