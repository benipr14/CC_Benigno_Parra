import os

from app.repositories.memory_repo import MemoryUserRepository

_default_repo = None


def _build_default_repo():
    """Create the default repository based on environment.

    Environment variables:
      REPO_TYPE: 'memory' (default) or 'mongo'
      MONGO_URI: Mongo connection string (optional)
      MONGO_DB: database name (optional)
    """
    repo_type = os.environ.get("REPO_TYPE", "memory").lower()
    if repo_type == "mongo":
        try:
            from pymongo import MongoClient
            from app.repositories.mongo_repo import MongoUserRepository

            uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
            db_name = os.environ.get("MONGO_DB", "CC")
            client = MongoClient(uri)
            return MongoUserRepository(client, db_name=db_name)
        except Exception:
            # fallback to memory repo if mongo not available
            return MemoryUserRepository()
    else:
        return MemoryUserRepository()


def get_user_repo():
    global _default_repo
    if _default_repo is None:
        _default_repo = _build_default_repo()
    return _default_repo
