import pytest
from unittest.mock import patch
from app.models.request_log import RequestLog


FAKE_INFERENCE = {
    "predicted_class": "canary",
    "confidence": 0.9123,
    "latency_ms": 85,
    "ram_mb": 12.4,
    "cpu_percent": 7.1,
}

FAKE_IMAGE = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64  # minimal non-empty bytes


@pytest.mark.asyncio
async def test_classify_inserts_request_log(client_with_auth, mock_session):
    """POST /classify must insert a RequestLog row into the session."""
    with patch("app.routers.classify.run_inference", return_value=FAKE_INFERENCE):
        async with client_with_auth as client:
            response = await client.post(
                "/classify",
                files={"file": ("bird.jpg", FAKE_IMAGE, "image/jpeg")},
                headers={"Authorization": "Bearer fake-token"},
            )

    assert response.status_code == 200
    # session.add must have been called with a RequestLog instance
    assert mock_session.add.called
    added = mock_session.add.call_args[0][0]
    assert isinstance(added, RequestLog)
    assert added.predicted_class == "canary"
    assert added.confidence == 0.9123
    assert added.user_id == "test-uid-123"
    assert added.image_filename == "bird.jpg"
    assert added.latency_ms == 85
    assert added.ram_mb == 12.4
    assert added.cpu_percent == 7.1
    assert mock_session.commit.called


@pytest.mark.asyncio
async def test_classify_requires_auth(client_no_auth):
    """POST /classify without a token must return 403."""
    async with client_no_auth as client:
        response = await client.post(
            "/classify",
            files={"file": ("bird.jpg", FAKE_IMAGE, "image/jpeg")},
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_requests_returns_history(client_with_auth, mock_session):
    """GET /requests returns the authenticated user's classification history."""
    from unittest.mock import MagicMock, AsyncMock

    fake_log = RequestLog(
        id=1,
        user_id="test-uid-123",
        image_filename="bird.jpg",
        predicted_class="canary",
        confidence=0.9123,
        latency_ms=85,
        ram_mb=12.4,
        cpu_percent=7.1,
        created_at=None,
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [fake_log]
    mock_session.execute = AsyncMock(return_value=mock_result)

    async with client_with_auth as client:
        response = await client.get(
            "/requests",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["predicted_class"] == "canary"
    assert data[0]["confidence"] == 0.9123
    assert data[0]["user_id"] == "test-uid-123"


@pytest.mark.asyncio
async def test_get_requests_requires_auth(client_no_auth):
    """GET /requests without a token must return 403."""
    async with client_no_auth as client:
        response = await client.get("/requests")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_classify_response_includes_metrics(client_with_auth, mock_session):
    """POST /classify response body must include a metrics object with latency, RAM, and CPU."""
    with patch("app.routers.classify.run_inference", return_value=FAKE_INFERENCE):
        async with client_with_auth as client:
            response = await client.post(
                "/classify",
                files={"file": ("bird.jpg", FAKE_IMAGE, "image/jpeg")},
                headers={"Authorization": "Bearer fake-token"},
            )

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data, "Response must contain a 'metrics' key"
    metrics = data["metrics"]
    assert metrics["latency_ms"] == 85
    assert metrics["ram_mb"] == 12.4
    assert metrics["cpu_percent"] == 7.1
