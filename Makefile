PY ?= python3
PIP ?= pip

.PHONY: test

# Crear/instalar dependencias en un virtualenv local
install:
	$(PY) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements-dev.txt

# Ejecutar tests
test:
	.venv/bin/python -m pytest -q
