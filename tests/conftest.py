import pytest
import mongomock

from app.repositories.mongo_repo import MongoUserRepository
from app.api.deps import get_user_repo
from app.api.main import app


@pytest.fixture
def mongo_client():
    """Provide a fresh mongomock client per test."""
    return mongomock.MongoClient()


@pytest.fixture
def mongo_repo(mongo_client):
    return MongoUserRepository(mongo_client, db_name="test_db")


@pytest.fixture
def client(mongo_repo):
    """TestClient that overrides the repository dependency to use mongomock-backed repo."""

    def _get_repo_override():
        return mongo_repo

    # override dependency (use the function object)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_user_repo] = _get_repo_override

    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
