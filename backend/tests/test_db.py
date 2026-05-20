import pytest
from app.database import Base


def test_base_exists():
    # Verify the declarative base is importable and has the expected interface
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")


def test_models_importable():
    from app.models.user import User
    from app.models.request_log import RequestLog
    assert User.__tablename__ == "users"
    assert RequestLog.__tablename__ == "requests"
