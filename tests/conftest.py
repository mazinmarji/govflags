from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.store import FlagStore


@pytest.fixture()
def store() -> FlagStore:
    return FlagStore()


@pytest.fixture()
def client(store: FlagStore) -> TestClient:
    app.dependency_overrides[get_store] = lambda: store
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
