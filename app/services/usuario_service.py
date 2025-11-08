from typing import Dict

from app.repositories.base import UserRepo
from app.exceptions import UserExistsError, NotFoundError


def crear_usuario(username: str, contrasenia: str, saldo: float, repo: UserRepo) -> str:
    """Create a new user using the provided repository.

    Raises UserExistsError if username already exists.
    """
    if repo.find_by_username(username):
        raise UserExistsError(f"Usuario '{username}' ya existe")
    if saldo is None:
        saldo = 0.0
    if saldo < 0:
        raise ValueError("Saldo no puede ser negativo")

    usuario = {"usuario": username, "contrasenia": contrasenia, "saldo": float(saldo), "apuestas": []}
    uid = repo.insertar_usuario(usuario)
    return uid


def obtener_usuario(uid: str, repo: UserRepo) -> Dict:
    u = repo.obtener_usuario(uid)
    if not u:
        raise NotFoundError(f"Usuario con id {uid} no encontrado")
    return u
