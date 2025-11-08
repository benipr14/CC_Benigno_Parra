from app.repositories.memory_repo import MemoryUserRepository
from app.services.partido_service import crear_partido, obtener_partido, cambiar_cuota_partido, termina_partido


def test_crear_y_obtener_partido():
    repo = MemoryUserRepository()
    pid = crear_partido("Local", "Visitante", 2.0, 3.0, 4.0, "2026-12-01", "12:00", "Pendiente", repo)
    assert pid is not None
    p = obtener_partido(pid, repo)
    assert p["local"] == "Local"


def test_cambiar_cuota():
    repo = MemoryUserRepository()
    pid = crear_partido("L", "V", 2.0, 3.0, 4.0, "2020-01-01", "12:00", "Pendiente", repo)
    ok = cambiar_cuota_partido(pid, "1", 2.5, repo)
    assert ok
    p = obtener_partido(pid, repo)
    assert p["cuota_local"] == 2.5


def test_termina_partido_y_liquida_apuestas():
    repo = MemoryUserRepository()
    uid = repo.insertar_usuario({"usuario": "gambler", "contrasenia": "pw", "saldo": 100.0})
    # use a past date so the partido can be finished by the service
    pid = crear_partido("L", "V", 2.0, 3.0, 4.0, "2000-01-01", "12:00", "Pendiente", repo)
    # place a bet of 30 (deducted)
    aid = repo.insertar_apuesta({"usuario_id": uid, "partido_id": pid, "elegido": "1", "cantidad": 30.0})
    repo.add_apuesta_to_usuario(uid, aid)
    repo.update_usuario_saldo(uid, 70.0)  # simulate deduction

    settled = termina_partido(pid, "1", repo)
    assert settled is not None
    assert aid in settled
    usuario = repo.obtener_usuario(uid)
    # saldo: 70 (after deduction) + 30*2.0 = 130
    assert usuario["saldo"] == 130.0
