from __future__ import annotations

import dataclasses
import decimal
import json
import time as time_module
from types import TracebackType
from typing import Annotated, Any, Self

import aio_request
import aiohttp
import marshmallow_recipe as mr

from finstats.contracts import DiffClient, ZenMoneyClientAuthException, ZenMoneyClientException, ZmDiffResponse, ZmTransaction

ENDPOINT = "https://api.zenmoney.app/v8/"

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


@dataclasses.dataclass(frozen=True, slots=True)
class ZmDiffRequest:
    server_timestamp: Annotated[int, mr.meta(name="serverTimestamp")]
    client_timestamp: Annotated[int, mr.meta(name="currentClientTimestamp")]
    transaction: list[ZmTransaction] = dataclasses.field(default_factory=list)


class ZenMoneyClient(DiffClient):
    _session: aiohttp.ClientSession | None
    _transport: aio_request.Transport | None
    _client: aio_request.Client | None

    def __init__(self) -> None:
        self._clean_client()

    async def __aenter__(self) -> Self:
        self.create_session()
        return self

    def create_session(self) -> None:
        if self._session is not None and not self._session.closed:
            return

        self._session = aiohttp.ClientSession()
        self._transport = aio_request.AioHttpTransport(self._session)  # ty:ignore[possibly-missing-attribute]
        self._client = aio_request.setup(transport=self._transport, endpoint=ENDPOINT)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.dispose()

    async def dispose(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._clean_client()

    def _clean_client(self) -> None:
        self._session = None
        self._transport = None
        self._client = None

    async def fetch_diff(self, token: str, server_timestamp: int, timeout_seconds: int = 20) -> ZmDiffResponse:
        return await self.sync_diff(
            token=token,
            diff_request=ZmDiffRequest(server_timestamp=server_timestamp, client_timestamp=int(time_module.time())),
            timeout_seconds=timeout_seconds,
        )

    async def sync_diff(self, token: str, diff_request: ZmDiffRequest, timeout_seconds: int = 20) -> ZmDiffResponse:
        if self._client is None:
            raise Exception("Cannot use not created session, consider using with")

        jsonDict = mr.dump(diff_request)
        jsonDict = self.hack_json_dict(jsonDict)

        response_ctx = self._client.request(
            aio_request.post(
                url="diff",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                body=json.dumps(jsonDict, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
            ),
            deadline=aio_request.Deadline.from_timeout(timeout_seconds),
        )
        async with response_ctx as response:
            if not response.is_successful():
                if response.status == 401:
                    raise ZenMoneyClientAuthException("Invalid token")
                exc_str = f"status code is {response.status}"
                response_error = await self.try_parse_error_from_response(response)
                if response_error:
                    exc_str += f" with response error: {response_error}"
                raise ZenMoneyClientException(exc_str)
            if not response.is_json:
                raise ZenMoneyClientException("Expected JSON object")

            data = await response.json(loads=lambda x: json.loads(x, parse_float=decimal.Decimal))

            if not isinstance(data, dict):
                raise ZenMoneyClientException("Expected JSON object")

            err = data.get("error")
            if err is not None:
                raise ZenMoneyClientException(f"Server method 'diff' returned error: {err!r}")

            return mr.load(ZmDiffResponse, data)

    async def try_parse_error_from_response(self, response: aio_request.Response) -> str | None:
        try:
            text = await response.text(encoding="utf-8")
        except aiohttp.ClientResponseError:
            return None
        return text

    @staticmethod
    def hack_json_dict(jsonDict: dict[str, Any]) -> dict[str, Any]:
        # Decimal fields from ZmTransaction that need to be converted to float for JSON
        decimal_keys = {"income", "outcome", "opIncome", "opOutcome"}

        for transaction in jsonDict.get("transaction", []):
            for key in decimal_keys:
                value = transaction.get(key)
                if value is None:
                    continue
                if isinstance(value, decimal.Decimal):
                    transaction[key] = float(value)
                elif isinstance(value, str):
                    transaction[key] = float(decimal.Decimal(value))

        return jsonDict
