from typing import Dict

from app.repositories.base import FullRepo
from app.exceptions import NotFoundError


def hacer_apuesta(usuario_id: str, partido_id: str, elegido: str, cantidad: float, repo: FullRepo):
    # basic validations
    usuario = repo.obtener_usuario(usuario_id)
    if not usuario:
        return None
    partido = repo.obtener_partido(partido_id)
    if not partido:
        return None
    # check saldo
    if usuario.get("saldo", 0.0) < cantidad:
        return None
    # deduct saldo
    nuevo = float(usuario.get("saldo", 0.0)) - float(cantidad)
    repo.update_usuario_saldo(usuario_id, nuevo)
    apuesta = {"usuario_id": usuario_id, "partido_id": partido_id, "elegido": elegido, "cantidad": float(cantidad)}
    aid = repo.insertar_apuesta(apuesta)
    repo.add_apuesta_to_usuario(usuario_id, aid)
    return aid


def obtener_apuesta(aid: str, repo: FullRepo):
    return repo.obtener_apuesta(aid)
