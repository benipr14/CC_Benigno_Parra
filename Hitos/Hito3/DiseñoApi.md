# diseño generald de la API
El disñeo general de la API es:

* Arquitectura por capas: La aplicación está organizada en capas bien separadas:
    app/api/: Routers (endpoints) y dependencias — interfaz HTTP.
    app/services/: Lógica de negocio (casos de uso) — sin conocimiento de HTTP.  
    app/repositories/: Abstracción de persistencia (protocols en base.py) + implementaciones (memory/mongo).
    app/models/: Pydantic schemas (DTOs) para validación entrada/salida.
    app/core/: configuración cross-cutting (logging).
* Principio central: los routers solo traducen HTTP <-> modelos y delegan toda la lógica a los servicios. Los servicios usan la abstracción de repositorio (FullRepo) sin acoplarse a la implementación concreta.

Cómo se consigue el desacoplo:

* Interface/Contrato: base.py define UserRepo/FullRepo (Protocol). Los servicios esperan FullRepo, no MongoUserRepository.
* Inyección de dependencias: deps.py expone get_user_repo() y las pruebas y despliegues pueden inyectar MemoryUserRepository o MongoUserRepository mediante la variable de entorno REPO_TYPE o con app.dependency_overrides.
* Modelos tipados: los routers usan Pydantic (schemas.py) para validar/normalizar entrada antes de pasar a servicios.
* Tests: los tests de integración sobrescriben la dependencia para inyectar mongomock o in-memory repos, demostrando que la API y el repositorio son intercambiables.

Rutas / tareas:

* Ping
    GET /ping — health check.
* Usuarios
    POST /api/v1/usuarios/ — crear usuario (payload: UsuarioCreate).
    GET /api/v1/usuarios/{uid} — obtener usuario (UsuarioOut).
* Partidos
    POST /api/v1/partidos/ — crear partido (PartidoCreate).
    GET /api/v1/partidos/{pid} — obtener partido (PartidoOut).
    POST /api/v1/partidos/{pid}/cuota — cambiar cuota.
    POST /api/v1/partidos/{pid}/resultado — terminar partido y liquidar apuestas.
* Apuestas
    POST /api/v1/apuestas/ — crear apuesta.
    GET /api/v1/apuestas/{aid} — obtener apuesta.

Errores y contratos:

* Los servicios devuelven resultados o lanzan/indican error por contrato; los routers traducen eso a códigos HTTP (400/404/201).

Tests y estrategia de verificación

* Tipos de tests:
    Unit tests: test_usuario_service.py, test_partido_service.py, test_apuesta_service.py — prueban lógica de negocio aislada con MemoryUserRepository.
    Integration tests (API): tests/test_api_*.py — usan FastAPI TestClient y sobrescriben dependencia con mongomock o MemoryUserRepository.
    Persistence tests (Mongo): tests/test_mongo_*.py — validan comportamiento de MongoUserRepository.
* Fixtures:
conftest.py define mongo_client, mongo_repo, client (TestClient que inyecta repo).

La estructura queda de la siguiente manera:
![Estructura API](imagenes/Estructura.png)