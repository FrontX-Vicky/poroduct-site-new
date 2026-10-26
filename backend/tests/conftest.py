import os
from pathlib import Path

# Separate test DB in database/, so tests never touch the real shop.db
TEST_DB = Path(__file__).resolve().parents[2] / "database" / "test_shop.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth(client):
    """Register a user and return Authorization headers for it."""
    res = client.post("/api/auth/register", json={"email": "test@example.com", "password": "secret123"})
    return {"Authorization": f"Bearer {res.json()['token']}"}


@pytest.fixture
def category(client, auth):
    return client.post("/api/categories", json={"name": "Books"}, headers=auth).json()
