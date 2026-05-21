import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_verify_token_raises_on_invalid():
    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("invalid")):
        with patch("firebase_admin.initialize_app"):
            from app.services.firebase import verify_token
            with pytest.raises(HTTPException) as exc:
                await verify_token(MagicMock(credentials="bad-token"))
            assert exc.value.status_code == 401
