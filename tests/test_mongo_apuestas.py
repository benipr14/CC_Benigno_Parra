def test_mongo_insert_and_get_apuesta(mongo_repo):
    # insert a partido first
    pid = mongo_repo.insertar_partido({
        "local": "A",
        "visitante": "B",
        "cuota_local": 2.0,
        "cuota_empate": 3.0,
        "cuota_visitante": 4.0,
        "fecha": "2020-01-01",
        "hora": "12:00",
        "resultado": "Pendiente",
    })
    apuesta = {"usuario_id": "u123", "partido_id": pid, "elegido": "1", "cantidad": 15.0}
    aid = mongo_repo.insertar_apuesta(apuesta)
    assert aid is not None
    fetched = mongo_repo.obtener_apuesta(aid)
    assert fetched is not None
    assert fetched["usuario_id"] == "u123"


def test_mongo_obtener_apuesta_invalid_id(mongo_repo):
    # invalid id should return None
    assert mongo_repo.obtener_apuesta("not-an-objectid") is None


def test_mongo_apuesta_linked_to_partido(mongo_repo):
    pid = mongo_repo.insertar_partido({
        "local": "C",
        "visitante": "D",
        "cuota_local": 2.5,
        "cuota_empate": 3.5,
        "cuota_visitante": 4.5,
        "fecha": "2020-01-01",
        "hora": "12:00",
        "resultado": "Pendiente",
    })
    a1 = mongo_repo.insertar_apuesta({"usuario_id": "u1", "partido_id": pid, "elegido": "1", "cantidad": 10.0})
    a2 = mongo_repo.insertar_apuesta({"usuario_id": "u2", "partido_id": pid, "elegido": "X", "cantidad": 5.0})
    apuestas = mongo_repo.get_apuestas_by_partido(pid)
    ids = {a["_id"] for a in apuestas}
    assert a1 in ids and a2 in ids
