import pytest

from client.client import FinstatsClient
from testing import testdata
from testing.zenmoney import FakeZenMoneyClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_correct_auth_token_should_return_200_with_ok(client: FinstatsClient) -> None:
    response = await client.get_transactions()
    assert response.total_count == len(testdata.TestTransactions)


async def test_correct_auth_token_should_return_401(client: FinstatsClient) -> None:
    with pytest.raises(Exception, match="status code is 401 with response error: Invalid Authorization token"):
        await client.get_transactions(token="error")


async def test_zm_client_raises_exception_should_return_500(zm_client: FakeZenMoneyClient, client: FinstatsClient) -> None:
    zm_client.set_response_code(408)

    with pytest.raises(Exception, match="status code is 500 with response error: Internal Server Error"):
        await client.get_transactions(token="error")
