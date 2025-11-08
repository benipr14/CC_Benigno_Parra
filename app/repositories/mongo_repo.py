from typing import Optional, Dict
from bson import ObjectId


class MongoUserRepository:
    """MongoDB-backed user repository. Works with real pymongo or mongomock clients.

    Methods return dictionaries with '_id' as a string to match in-memory repo shape.
    """

    def __init__(self, client, db_name: str = "CC"):
        self._db = client[db_name]
        self._col = self._db["usuarios"]

    def insertar_usuario(self, usuario: Dict) -> str:
        # Ensure we don't pass any string _id accidentally
        doc = dict(usuario)
        doc.pop("_id", None)
        res = self._col.insert_one(doc)
        return str(res.inserted_id)

    # --- partidos -------------------------------------------------
    def insertar_partido(self, partido: Dict) -> str:
        doc = dict(partido)
        doc.pop("_id", None)
        res = self._db["partidos"].insert_one(doc)
        return str(res.inserted_id)

    def obtener_partido(self, pid: str) -> Optional[Dict]:
        try:
            oid = ObjectId(pid)
        except Exception:
            return None
        doc = self._db["partidos"].find_one({"_id": oid})
        if not doc:
            return None
        doc = dict(doc)
        doc["_id"] = str(doc["_id"])
        return doc

    def update_partido(self, pid: str, patch: Dict) -> bool:
        try:
            oid = ObjectId(pid)
        except Exception:
            return False
        res = self._db["partidos"].update_one({"_id": oid}, {"$set": patch})
        return res.modified_count > 0

    # --- apuestas -------------------------------------------------
    def insertar_apuesta(self, apuesta: Dict) -> str:
        doc = dict(apuesta)
        doc.pop("_id", None)
        res = self._db["apuestas"].insert_one(doc)
        return str(res.inserted_id)

    def obtener_apuesta(self, aid: str) -> Optional[Dict]:
        try:
            oid = ObjectId(aid)
        except Exception:
            return None
        doc = self._db["apuestas"].find_one({"_id": oid})
        if not doc:
            return None
        doc = dict(doc)
        doc["_id"] = str(doc["_id"])
        return doc

    def get_apuestas_by_partido(self, partido_id: str) -> list:
        docs = list(self._db["apuestas"].find({"partido_id": partido_id}))
        results = []
        for d in docs:
            dd = dict(d)
            dd["_id"] = str(dd["_id"])
            results.append(dd)
        return results

    # usuario helpers
    def update_usuario_saldo(self, uid: str, nuevo_saldo: float) -> bool:
        try:
            oid = ObjectId(uid)
        except Exception:
            return False
        res = self._col.update_one({"_id": oid}, {"$set": {"saldo": float(nuevo_saldo)}})
        return res.modified_count > 0

    def add_apuesta_to_usuario(self, uid: str, aid: str) -> None:
        # push apuesta id (string) into user's apuestas array
        try:
            oid = ObjectId(uid)
        except Exception:
            return
        self._col.update_one({"_id": oid}, {"$push": {"apuestas": aid}})

    def obtener_usuario(self, uid: str) -> Optional[Dict]:
        try:
            oid = ObjectId(uid)
        except Exception:
            return None
        doc = self._col.find_one({"_id": oid})
        if not doc:
            return None
        doc = dict(doc)
        doc["_id"] = str(doc["_id"])
        return doc

    def find_by_username(self, username: str) -> Optional[Dict]:
        doc = self._col.find_one({"usuario": username})
        if not doc:
            return None
        doc = dict(doc)
        doc["_id"] = str(doc["_id"])
        return doc
