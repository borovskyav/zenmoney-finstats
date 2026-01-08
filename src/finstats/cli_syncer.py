from finstats.contracts import DiffClient, Syncer, ZmDiffResponse
from finstats.file import parse_and_validate_path, write_content_to_file


class CliSyncer(Syncer):
    _client: DiffClient

    def __init__(self, client: DiffClient) -> None:
        self._client = client

    async def dry_run(self, timestamp: int, out: str) -> ZmDiffResponse:
        path = parse_and_validate_path(out)
        response = await self._client.fetch_diff(timestamp)
        print(response.server_timestamp)
        print(len(response.transaction))
        write_content_to_file(path, response)
        return response
