from pathlib import Path

import sqlalchemy.ext.asyncio as sa_async

from finstats.contracts import DiffClient, ZmDiffResponse
from finstats.file import parse_and_validate_path, write_content_to_file
from finstats.store.psql_store import get_last_timestamp, save_diff


class CliSyncer:
    _client: DiffClient
    _conn: sa_async.AsyncConnection

    def __init__(self, client: DiffClient, conn: sa_async.AsyncConnection) -> None:
        self._client = client
        self._conn = conn

    async def dry_run(self, timestamp: int, out: str) -> None:
        path = parse_and_validate_path(out)
        diff = await self._fetch_diff_and_print(timestamp)
        write_content_to_file(path, diff)

    async def sync_once(self) -> None:
        timestamp = await get_last_timestamp(self._conn)
        print(timestamp)
        diff = await self._fetch_diff_and_print(timestamp)
        write_content_to_file(Path("file.json"), diff)
        await save_diff(self._conn, diff)

    async def _fetch_diff_and_print(self, timestamp: int) -> ZmDiffResponse:
        diff = await self._client.fetch_diff(timestamp)
        print(
            f"transactions: {len(diff.transaction)}, "
            f"deleted: {sum(t.deleted for t in diff.transaction)}, "
            f"new: {sum(not t.deleted and not t.viewed for t in diff.transaction)}"
        )
        return diff
