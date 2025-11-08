def test_mongo_repo_insert_and_get(mongo_repo):
    usuario = {"usuario": "mongo_user", "contrasenia": "pw", "saldo": 55.0}
    uid = mongo_repo.insertar_usuario(usuario)
    assert uid is not None
    fetched = mongo_repo.obtener_usuario(uid)
    assert fetched is not None
    assert fetched["usuario"] == "mongo_user"


def test_mongo_repo_find_by_username(mongo_repo):
    usuario = {"usuario": "findme", "contrasenia": "pw", "saldo": 10.0}
    uid = mongo_repo.insertar_usuario(usuario)
    found = mongo_repo.find_by_username("findme")
    assert found is not None
    assert found["_id"] == uid
