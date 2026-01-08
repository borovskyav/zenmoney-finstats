from __future__ import annotations

import dataclasses
import decimal
import json
import time as time_module
from types import TracebackType
from typing import Annotated, Self

import aio_request
import aiohttp
import marshmallow_recipe as mr

from finstats.contracts import DiffClient, ZmDiffResponse

ENDPOINT = "https://api.zenmoney.app/v8/"

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


class ZenMoneyClientException(Exception):
    pass


@dataclasses.dataclass(frozen=True, slots=True)
class ZmDiffRequest:
    server_timestamp: Annotated[int, mr.meta(name="serverTimestamp")]
    client_timestamp: Annotated[int, mr.meta(name="currentClientTimestamp")]


class ZenMoneyClient(DiffClient):
    _api_key: str
    _session: aiohttp.ClientSession | None
    _transport: aio_request.Transport | None
    _client: aio_request.Client | None

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._clean_client()

    async def __aenter__(self) -> Self:
        self._session = aiohttp.ClientSession()
        self._transport = aio_request.AioHttpTransport(self._session)  # ty:ignore[possibly-missing-attribute]
        self._client = aio_request.setup(transport=self._transport, endpoint=ENDPOINT)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is not None:
            await self._session.close()
            self._clean_client()

    def _clean_client(self) -> None:
        self._session = None
        self._transport = None
        self._client = None

    async def fetch_diff(self, server_timestamp: int) -> ZmDiffResponse:
        api_key = self._api_key

        if self._client is None:
            raise Exception("Cannot use not created session, consider using with")

        req = ZmDiffRequest(server_timestamp=server_timestamp, client_timestamp=int(time_module.time()))

        response_ctx = self._client.request(
            aio_request.post(
                url="diff",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                body=json.dumps(mr.dump(req), separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
            ),
            deadline=aio_request.Deadline.from_timeout(5),
        )
        async with response_ctx as response:
            if not response.is_successful():
                raise ZenMoneyClientException(f"status code is {response.status}")
            if not response.is_json:
                raise ZenMoneyClientException("Expected JSON object")

            data = await response.json(loads=lambda x: json.loads(x, parse_float=decimal.Decimal))

            if not isinstance(data, dict):
                raise ZenMoneyClientException("Expected JSON object")

            err = data.get("error")
            if err is not None:
                raise ZenMoneyClientException(f"Server method 'diff' returned error: {err!r}")

            return mr.load(ZmDiffResponse, data)
