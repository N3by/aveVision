import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client_no_auth):
    async with client_no_auth as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
