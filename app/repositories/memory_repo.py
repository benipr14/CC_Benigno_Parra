import uuid
from typing import Dict, Optional, Any


class MemoryUserRepository:
    """In-memory repository for users (for tests and simple development)."""

    def __init__(self):
        self._users: Dict[str, Dict] = {}
        self._partidos: Dict[str, Dict] = {}
        self._apuestas: Dict[str, Dict] = {}

    def insertar_usuario(self, usuario: Dict) -> str:
        # usuario expected to contain 'usuario', 'contrasenia', 'saldo'
        uid = str(uuid.uuid4())
        # store a shallow copy with defaults
        record = {
            "_id": uid,
            "usuario": usuario.get("usuario"),
            "contrasenia": usuario.get("contrasenia"),
            "saldo": usuario.get("saldo", 0.0),
            "apuestas": usuario.get("apuestas", []),
        }
        self._users[uid] = record
        return uid

    def obtener_usuario(self, uid: str) -> Optional[Dict]:
        return self._users.get(uid)

    def find_by_username(self, username: str) -> Optional[Dict]:
        for u in self._users.values():
            if u.get("usuario") == username:
                return u
        return None

    # --- partidos -------------------------------------------------
    def insertar_partido(self, partido: Dict) -> str:
        pid = str(uuid.uuid4())
        record = dict(partido)
        record.setdefault("resultado", "Pendiente")
        record["_id"] = pid
        self._partidos[pid] = record
        return pid

    def obtener_partido(self, pid: str) -> Optional[Dict]:
        return self._partidos.get(pid)

    def update_partido(self, pid: str, patch: Dict[str, Any]) -> bool:
        p = self._partidos.get(pid)
        if not p:
            return False
        p.update(patch)
        return True

    # --- apuestas ------------------------------------------------
    def insertar_apuesta(self, apuesta: Dict) -> str:
        aid = str(uuid.uuid4())
        rec = dict(apuesta)
        rec["_id"] = aid
        self._apuestas[aid] = rec
        return aid

    def obtener_apuesta(self, aid: str) -> Optional[Dict]:
        return self._apuestas.get(aid)

    def get_apuestas_by_partido(self, partido_id: str) -> list:
        return [a for a in self._apuestas.values() if a.get("partido_id") == partido_id]

    # usuario helpers
    def update_usuario_saldo(self, uid: str, nuevo_saldo: float) -> bool:
        u = self._users.get(uid)
        if not u:
            return False
        u["saldo"] = float(nuevo_saldo)
        return True

    def add_apuesta_to_usuario(self, uid: str, aid: str) -> None:
        u = self._users.get(uid)
        if not u:
            return
        u.setdefault("apuestas", []).append(aid)
