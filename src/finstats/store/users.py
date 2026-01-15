from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import ZmUser
from finstats.store.base import UserTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses


class UsersRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def save_users(self, users: list[ZmUser]) -> None:
        if not users:
            return

        stmt = sa_postgresql.insert(UserTable).values(from_dataclasses(users))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in UserTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[UserTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)
