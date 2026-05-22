import pytest
from unittest.mock import MagicMock, patch, AsyncMock
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
