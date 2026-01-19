from __future__ import annotations

import decimal
import json

import aio_request
import aiohttp
import marshmallow_recipe as mr

from finstats.domain import ZenmoneyDiff
from finstats.zenmoney.convert import diff_to_zm_diff, zm_diff_to_diff
from finstats.zenmoney.models import ZenMoneyClientAuthException, ZenMoneyClientException, ZmDiffResponse

ENDPOINT = "https://api.zenmoney.app/v8/"

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


class ZenMoneyClient:
    def __init__(self) -> None:
        self._session = aiohttp.ClientSession()
        self._transport = aio_request.AioHttpTransport(self._session)  # ty:ignore[possibly-missing-attribute]
        self._client = aio_request.setup(transport=self._transport, endpoint=ENDPOINT)

    async def dispose(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None
            self._transport = None
            self._client = None

    async def sync_diff(self, token: str, diff: ZenmoneyDiff, timeout_seconds: int = 20) -> ZenmoneyDiff:
        if self._client is None:
            raise Exception("Cannot use not created session, consider using with")

        diff_request = diff_to_zm_diff(diff)
        response_ctx = self._client.request(
            aio_request.post(
                url="diff",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                body=json.dumps(mr.dump(diff_request), separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
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

            diff_response = mr.load(ZmDiffResponse, data)
            return zm_diff_to_diff(diff_response)

    @staticmethod
    async def try_parse_error_from_response(response: aio_request.Response) -> str | None:
        try:
            text = await response.text(encoding="utf-8")
        except aiohttp.ClientResponseError:
            return None
        return text
