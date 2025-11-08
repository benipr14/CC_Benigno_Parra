from app.repositories.memory_repo import MemoryUserRepository
from app.services.usuario_service import crear_usuario
from app.services.partido_service import crear_partido
from app.services.apuesta_service import hacer_apuesta, obtener_apuesta


def test_hacer_apuesta_y_obtener():
    repo = MemoryUserRepository()
    uid = crear_usuario("apostador", "pw", 100.0, repo)
    pid = crear_partido("L", "V", 2.0, 3.0, 4.0, "2026-12-01", "12:00", "Pendiente", repo)
    aid = hacer_apuesta(uid, pid, "1", 20.0, repo)
    assert aid is not None
    a = obtener_apuesta(aid, repo)
    assert a["usuario_id"] == uid
    # saldo decreased
    u = repo.obtener_usuario(uid)
    assert u["saldo"] == 80.0


def test_hacer_apuesta_sin_saldo():
    repo = MemoryUserRepository()
    uid = crear_usuario("poor", "pw", 10.0, repo)
    pid = crear_partido("L", "V", 2.0, 3.0, 4.0, "2026-12-01", "12:00", "Pendiente", repo)
    aid = hacer_apuesta(uid, pid, "1", 20.0, repo)
    assert aid is None
