import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_sync_user_requires_auth(client_no_auth):
    """Request with no Authorization header must return 403."""
    async with client_no_auth as client:
        response = await client.post("/auth/sync", json={
            "firebase_uid": "uid-123",
            "email": "test@example.com",
        })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_sync_user_creates_user(client_with_auth, mock_session):
    """Valid token + new user → 200 with user data."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    async def set_role(user):
        user.role = "user"

    mock_session.refresh.side_effect = set_role

    async with client_with_auth as client:
        response = await client.post(
            "/auth/sync",
            json={"firebase_uid": "test-uid-123", "email": "test@example.com"},
            headers={"Authorization": "Bearer fake-token"},
        )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
