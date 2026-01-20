import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.domain import Tag, TagId
from finstats.store.base import TagTable
from finstats.store.connection import ConnectionScope
from finstats.store.misc import from_dataclasses, to_dataclass, to_dataclasses


class TagsRepository:
    __connection_scope: ConnectionScope

    def __init__(self, connection: ConnectionScope) -> None:
        self.__connection_scope = connection

    async def get_tag(self, tag_id: TagId) -> Tag | None:
        stmt = sa.select(TagTable).where(TagTable.id == tag_id)
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclass(Tag, result.one_or_none())

    async def get_tags(self) -> list[Tag]:
        stmt = sa.select(TagTable)
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(Tag, result.all())

    async def get_children_tags(self, parent_tag_id: TagId) -> list[Tag]:
        stmt = sa.select(TagTable).where(TagTable.parent == parent_tag_id)
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(Tag, result.all())

    async def get_tags_by_id(self, tag_ids: list[TagId]) -> list[Tag]:
        if not tag_ids:
            return []
        stmt = sa.select(TagTable).where(TagTable.id.in_(tag_ids))
        async with self.__connection_scope.acquire() as connection:
            result = await connection.execute(stmt)
            return to_dataclasses(Tag, result.all())

    async def save_tags(self, tags: list[Tag]) -> None:
        if not tags:
            return

        stmt = sa_postgresql.insert(TagTable).values(from_dataclasses(tags))
        excluded = stmt.excluded
        set_cols = {c.name: getattr(excluded, c.name) for c in TagTable.__table__.columns if c.name != "id"}

        async with self.__connection_scope.acquire() as connection:
            stmt = stmt.on_conflict_do_update(
                index_elements=[TagTable.id],
                set_=set_cols,
            )
            await connection.execute(stmt)
