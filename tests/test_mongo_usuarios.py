def test_create_and_get_usuario_mongo(client):
    payload = {"usuario": "maria", "contrasenia": "pw", "saldo": 50.0}
    r = client.post("/api/v1/usuarios/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert "_id" in data
    uid = data["_id"]

    r2 = client.get(f"/api/v1/usuarios/{uid}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["usuario"] == "maria"
    assert float(body["saldo"]) == 50.0
