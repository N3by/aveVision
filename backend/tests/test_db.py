import pytest
from app.database import Base


def test_base_exists():
    # Verify the declarative base is importable and has the expected interface
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")
