from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.api.deps import get_user_repo
from app.repositories.memory_repo import MemoryUserRepository


@pytest.fixture
def repo():
    return MemoryUserRepository()


@pytest.fixture
def client(repo):
    # override dependency to use a fresh in-memory repo per test
    def _get_repo():
        return repo

    app.dependency_overrides.clear()
    app.dependency_overrides[get_user_repo] = _get_repo
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_and_get_usuario(client):
    payload = {"usuario": "juan", "contrasenia": "pw", "saldo": 120.0}
    r = client.post("/api/v1/usuarios/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert "_id" in data
    uid = data["_id"]

    r2 = client.get(f"/api/v1/usuarios/{uid}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["usuario"] == "juan"
    assert float(body["saldo"]) == 120.0
