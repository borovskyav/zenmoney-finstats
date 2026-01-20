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


class ZenMoneyClient:
    __slots__ = (
        "__client",
        "__transport",
        "__session",
    )

    def __init__(self) -> None:
        self.__session = aiohttp.ClientSession()
        self.__transport = aio_request.AioHttpTransport(self.__session)  # ty:ignore[possibly-missing-attribute]
        self.__client = aio_request.setup(transport=self.__transport, endpoint=ENDPOINT)

    async def dispose(self) -> None:
        if self.__session is not None and not self.__session.closed:
            await self.__session.close()
            self.__session = None
            self.__transport = None
            self.__client = None

    async def sync_diff(self, token: str, diff: ZenmoneyDiff, timeout_seconds: int = 20) -> ZenmoneyDiff:
        if self.__client is None:
            raise Exception("Cannot use not created session, consider using with")

        diff_request = diff_to_zm_diff(diff)
        request_data = mr.dump(diff_request, naming_case=mr.CAMEL_CASE)
        request_body = json.dumps(request_data, default=_json_default, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        response_ctx = self.__client.request(
            aio_request.post(
                url="diff",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                body=request_body,
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

            diff_response = mr.load(ZmDiffResponse, data, naming_case=mr.CAMEL_CASE)
            return zm_diff_to_diff(diff_response)

    @staticmethod
    async def try_parse_error_from_response(response: aio_request.Response) -> str | None:
        try:
            text = await response.text(encoding="utf-8")
        except aiohttp.ClientResponseError:
            return None
        return text


def _json_default(obj: object) -> float:
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
