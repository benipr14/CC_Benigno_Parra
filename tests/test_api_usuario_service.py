import pytest

from app.repositories.memory_repo import MemoryUserRepository
from app.services.usuario_service import crear_usuario, obtener_usuario
from app.exceptions import UserExistsError, NotFoundError


def test_crear_usuario_exitoso():
    repo = MemoryUserRepository()
    uid = crear_usuario("juan", "pw", 100.0, repo)
    assert uid is not None
    usuario = repo.obtener_usuario(uid)
    assert usuario["usuario"] == "juan"
    assert usuario["saldo"] == 100.0


def test_crear_usuario_duplicado():
    repo = MemoryUserRepository()
    crear_usuario("ana", "pw", 50.0, repo)
    with pytest.raises(UserExistsError):
        crear_usuario("ana", "pw2", 20.0, repo)


def test_crear_usuario_saldo_negativo():
    repo = MemoryUserRepository()
    with pytest.raises(ValueError):
        crear_usuario("pepe", "pw", -10.0, repo)


def test_obtener_usuario_no_encontrado():
    repo = MemoryUserRepository()
    with pytest.raises(NotFoundError):
        obtener_usuario("no-existe", repo)
