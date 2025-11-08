PY ?= python3
PIP ?= pip

.PHONY: test install clean finish-partido test-integration test-all

# Crear/instalar dependencias en un virtualenv local
install:
	$(PY) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements-dev.txt

# Ejecutar tests
test:
	.venv/bin/python -m pytest -q

# Ejecutar tests de integración (API y pruebas que usan Mongo/mongomock)
test-integration:
	.venv/bin/python -m pytest -q tests/test_api_*.py tests/test_mongo*.py tests/test_ping.py

# Ejecutar todos los tests (unidad + integración) y el caso específico finish-partido
test-all:
	$(MAKE) test
	$(MAKE) test-integration

# Limpiar artefactos locales y el virtualenv (.venv)
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info