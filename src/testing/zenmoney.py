from finstats.domain import ZenmoneyDiff
from finstats.zenmoney import ZenMoneyClient, ZenMoneyClientAuthException, ZenMoneyClientException


class FakeZenMoneyClient(ZenMoneyClient):
    __response_code: int = 200

    async def sync_diff(self, token: str, diff: ZenmoneyDiff, timeout_seconds: int = 20) -> ZenmoneyDiff:
        if self.__response_code != 200:
            exc_str = f"status code is {self.__response_code}"
            raise ZenMoneyClientException(exc_str)

        if token != "ok":
            raise ZenMoneyClientAuthException("Invalid token")

        return ZenmoneyDiff(
            server_timestamp=diff.server_timestamp,
            transactions=[],
            accounts=[],
            companies=[],
            countries=[],
            instruments=[],
            merchants=[],
            tags=[],
            users=[],
        )

    def set_response_code(self, code: int) -> None:
        self.__response_code = code

    def cleanup(self) -> None:
        self.__response_code: int = 200
