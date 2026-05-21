import os
os.environ["TESTING"] = "1"

import pytest
from unittest.mock import MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app.database import get_db
from app.services.firebase import verify_token


def make_mock_session():
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def client_with_auth(mock_session):
    """Test client with Firebase auth and DB both overridden."""
    async def override_get_db():
        yield mock_session

    def override_verify_token():
        return {"uid": "test-uid-123", "email": "test@example.com"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_token] = override_verify_token
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth():
    """Test client with no auth override (tests unauthenticated paths)."""
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
