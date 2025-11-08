def test_mongo_partido_insert_and_get(mongo_repo):
    partido = {
        "local": "MongoL",
        "visitante": "MongoV",
        "cuota_local": 2.1,
        "cuota_empate": 3.3,
        "cuota_visitante": 4.4,
        "fecha": "2025-01-01",
        "hora": "15:00",
        "resultado": "Pendiente",
    }
    pid = mongo_repo.insertar_partido(partido)
    assert pid is not None
    fetched = mongo_repo.obtener_partido(pid)
    assert fetched is not None
    assert fetched["local"] == "MongoL"


def test_mongo_partido_update(mongo_repo):
    partido = {
        "local": "UpdL",
        "visitante": "UpdV",
        "cuota_local": 2.0,
        "cuota_empate": 3.0,
        "cuota_visitante": 4.0,
        "fecha": "2020-01-01",
        "hora": "12:00",
        "resultado": "Pendiente",
    }
    pid = mongo_repo.insertar_partido(partido)
    ok = mongo_repo.update_partido(pid, {"cuota_local": 5.5})
    assert ok
    fetched = mongo_repo.obtener_partido(pid)
    assert float(fetched["cuota_local"]) == 5.5


def test_mongo_get_apuestas_by_partido(mongo_repo):
    partido = {
        "local": "BetL",
        "visitante": "BetV",
        "cuota_local": 2.0,
        "cuota_empate": 3.0,
        "cuota_visitante": 4.0,
        "fecha": "2020-01-01",
        "hora": "12:00",
        "resultado": "Pendiente",
    }
    pid = mongo_repo.insertar_partido(partido)
    a1 = mongo_repo.insertar_apuesta({"usuario_id": "u1", "partido_id": pid, "elegido": "1", "cantidad": 10.0})
    a2 = mongo_repo.insertar_apuesta({"usuario_id": "u2", "partido_id": pid, "elegido": "2", "cantidad": 5.0})
    res = mongo_repo.get_apuestas_by_partido(pid)
    ids = [r["_id"] for r in res]
    assert a1 in ids and a2 in ids
