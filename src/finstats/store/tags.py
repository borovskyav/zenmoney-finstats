import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from sqlalchemy.dialects import postgresql as sa_postgresql

from finstats.contracts import TagId, ZmTag
from finstats.store.base import TagTable
from finstats.store.misc import from_dataclasses, to_dataclasses


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


async def get_tags(connection: sa_async.AsyncConnection) -> list[ZmTag]:
    stmt = sa.select(TagTable)
    result = await connection.execute(stmt)
    rows = result.all()
    return to_dataclasses(ZmTag, rows)


async def get_children_tags(connection: sa_async.AsyncConnection, parent_tag_id: TagId) -> list[ZmTag]:
    stmt = sa.select(TagTable).where(TagTable.parent == parent_tag_id)
    result = await connection.execute(stmt)
    rows = result.all()
    return to_dataclasses(ZmTag, rows)


async def get_tags_by_id(connection: sa_async.AsyncConnection, tag_ids: list[TagId]) -> list[ZmTag]:
    stmt = sa.select(TagTable).where(TagTable.id.in_(tag_ids))
    result = await connection.execute(stmt)
    rows = result.all()
    return to_dataclasses(ZmTag, rows)


async def get_tag(connection: sa_async.AsyncConnection, tag_id: TagId) -> ZmTag | None:
    tags = await get_tags_by_id(connection, [tag_id])
    return None if not tags else tags[0]
