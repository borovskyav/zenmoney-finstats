from finstats.contracts import DiffClient, Store, Syncer
from finstats.file import parse_and_validate_path, write_content_to_file


class CliSyncer(Syncer):
    _client: DiffClient

    def __init__(self, client: DiffClient, store: Store) -> None:
        self._client = client
        self._store = store

    async def dry_run(self, timestamp: int, out: str) -> None:
        path = parse_and_validate_path(out)
        diff = await self._client.fetch_diff(timestamp)
        print(f"timestamp: {diff.server_timestamp}")
        print(f"transactions: {len(diff.transaction)}, deleted: {sum(t.deleted for t in diff.transaction)}")
        write_content_to_file(path, diff)

    async def sync_once(self) -> None:
        timestamp = await self._store.get_last_timestamp()
        diff = await self._client.fetch_diff(timestamp)
        print(f"timestamp: {diff.server_timestamp}")
        print(f"transactions: {len(diff.transaction)}, deleted: {sum(t.deleted for t in diff.transaction)}")
        await self._store.save_diff(diff)
