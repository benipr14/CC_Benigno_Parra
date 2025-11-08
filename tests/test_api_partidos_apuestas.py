def test_create_partido_and_change_cuota(client):
    # create partido
    payload = {
        "local": "TeamA",
        "visitante": "TeamB",
        "cuota_local": 2.0,
        "cuota_empate": 3.0,
        "cuota_visitante": 4.0,
        "fecha": "2026-12-01",
        "hora": "12:00",
    }
    r = client.post("/api/v1/partidos/", json=payload)
    assert r.status_code == 201
    pid = r.json().get("_id")

    # get partido
    r2 = client.get(f"/api/v1/partidos/{pid}")
    assert r2.status_code == 200
    partido = r2.json()
    assert partido["local"] == "TeamA"

    # change cuota
    r3 = client.post(f"/api/v1/partidos/{pid}/cuota", json={"condicion": "1", "nueva": 2.5})
    assert r3.status_code == 200
    r4 = client.get(f"/api/v1/partidos/{pid}")
    assert r4.json()["cuota_local"] == 2.5


def test_create_apuesta_via_api(client):
    # create user
    u = {"usuario": "betuser", "contrasenia": "pw", "saldo": 100.0}
    ru = client.post("/api/v1/usuarios/", json=u)
    assert ru.status_code == 201
    uid = ru.json()["_id"]

    # create partido
    p = {
        "local": "L",
        "visitante": "V",
        "cuota_local": 2.0,
        "cuota_empate": 3.0,
        "cuota_visitante": 4.0,
        "fecha": "2099-01-01",
        "hora": "12:00",
    }
    rp = client.post("/api/v1/partidos/", json=p)
    assert rp.status_code == 201
    pid = rp.json()["_id"]

    # place a valid bet
    bet = {"usuario_id": uid, "partido_id": pid, "elegido": "1", "cantidad": 20.0}
    rb = client.post("/api/v1/apuestas/", json=bet)
    assert rb.status_code == 201
    aid = rb.json().get("_id")

    # get apuesta
    rg = client.get(f"/api/v1/apuestas/{aid}")
    assert rg.status_code == 200
    data = rg.json()
    assert data["usuario_id"] == uid
    assert data["partido_id"] == pid


def test_create_apuesta_insufficient_funds(client):
    # create poor user
    u = {"usuario": "pooruser", "contrasenia": "pw", "saldo": 5.0}
    ru = client.post("/api/v1/usuarios/", json=u)
    uid = ru.json()["_id"]

    # create partido
    p = {
        "local": "L2",
        "visitante": "V2",
        "cuota_local": 2.0,
        "cuota_empate": 3.0,
        "cuota_visitante": 4.0,
        "fecha": "2099-01-01",
        "hora": "12:00",
    }
    rp = client.post("/api/v1/partidos/", json=p)
    pid = rp.json()["_id"]

    bet = {"usuario_id": uid, "partido_id": pid, "elegido": "1", "cantidad": 20.0}
    rb = client.post("/api/v1/apuestas/", json=bet)
    assert rb.status_code == 400


def test_finish_partido_and_settle_via_api(client):
    # create user
    u = {"usuario": "settleuser", "contrasenia": "pw", "saldo": 100.0}
    ru = client.post("/api/v1/usuarios/", json=u)
    assert ru.status_code == 201
    uid = ru.json()['_id']

    # create partido in the past so it can be finished
    p = {
        "local": "PastL",
        "visitante": "PastV",
        "cuota_local": 2.0,
        "cuota_empate": 3.0,
        "cuota_visitante": 4.0,
        "fecha": "2000-01-01",
        "hora": "12:00",
    }
    rp = client.post("/api/v1/partidos/", json=p)
    assert rp.status_code == 201
    pid = rp.json()['_id']

    # place a bet on local ("1") for 10.0
    bet = {"usuario_id": uid, "partido_id": pid, "elegido": "1", "cantidad": 10.0}
    rb = client.post("/api/v1/apuestas/", json=bet)
    assert rb.status_code == 201

    # finish partido via API
    rf = client.post(f"/api/v1/partidos/{pid}/resultado", json={"resultado": "1"})
    assert rf.status_code == 200
    data = rf.json()
    assert "liquidadas" in data
    assert isinstance(data["liquidadas"], list)

    # check user's new balance: initial 100 - stake 10 + winnings (10 * cuota_local 2.0) = 100 -10 +20 = 110
    gu = client.get(f"/api/v1/usuarios/{uid}")
    assert gu.status_code == 200
    usuario = gu.json()
    assert usuario["saldo"] == 110.0
