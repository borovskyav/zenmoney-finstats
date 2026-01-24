import pytest
from aiohttp.test_utils import TestClient

from testing.zenmoney import FakeZenMoneyClient

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_health_should_return_ok(client: TestClient) -> None:
    resp = await client.get("/health")
    assert resp.status == 200
    data = await resp.json()
    assert data["api"] == "ok"
    assert data["last_synced_timestamp"] == "0"


async def test_correct_auth_token_should_ok(client: TestClient) -> None:
    resp = await client.get("/api/v1/transactions", headers={"Authorization": "ok"})
    assert resp.status == 200
    data = await resp.json()
    assert data["total_count"] == 0


async def test_correct_auth_token_should_return_401(client: TestClient) -> None:
    resp = await client.get("/api/v1/transactions", headers={"Authorization": "error"})
    assert resp.status == 401
    data = await resp.json()
    assert data["message"] == "Invalid Authorization token"


async def test_zm_client_raises_exception_should_return_500(zm_client: FakeZenMoneyClient, client: TestClient) -> None:
    zm_client.set_response_code(408)

    resp = await client.get("/api/v1/transactions", headers={"Authorization": "ok"})
    assert resp.status == 500
    data = await resp.json()
    assert data["message"] == "Internal Server Error"
