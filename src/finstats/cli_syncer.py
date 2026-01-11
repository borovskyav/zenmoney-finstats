from pathlib import Path
from types import TracebackType
from typing import Self

import sqlalchemy.ext.asyncio as sa_async

from finstats.client import ZenMoneyClient
from finstats.contracts import ZmDiffResponse
from finstats.file import parse_and_validate_path, write_content_to_file
from finstats.store.base import create_engine
from finstats.store.psql_store import get_last_timestamp, save_diff


class CliSyncer:
    _client: ZenMoneyClient
    _engine: sa_async.AsyncEngine
    _token: str

    def __init__(self, token: str) -> None:
        self._token = token

    async def __aenter__(self) -> Self:
        self._engine = create_engine()
        self._client = ZenMoneyClient()
        self._client.create_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._engine is not None:
            await self._engine.dispose()
        if self._client is not None:
            await self._client.dispose()

    async def dry_run(self, timestamp: int, out: str) -> None:
        path = parse_and_validate_path(out)
        diff = await self._fetch_diff_and_print(timestamp)
        write_content_to_file(path, diff)

    async def sync_once(self) -> None:
        async with self._engine.begin() as conn:
            timestamp = await get_last_timestamp(conn)
            print(timestamp)
            diff = await self._fetch_diff_and_print(timestamp)
            write_content_to_file(Path("file.json"), diff)
            await save_diff(conn, diff)

    async def _fetch_diff_and_print(self, timestamp: int) -> ZmDiffResponse:
        diff = await self._client.fetch_diff(self._token, timestamp)
        print(
            f"transactions: {len(diff.transaction)}, "
            f"deleted: {sum(t.deleted for t in diff.transaction)}, "
            f"new: {sum(not t.deleted and not t.viewed for t in diff.transaction)}"
        )
        return diff
