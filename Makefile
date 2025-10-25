PY ?= python3
PIP ?= pip

.PHONY: test install clean

# Crear/instalar dependencias en un virtualenv local
install:
	$(PY) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements-dev.txt

# Ejecutar tests
test:
	.venv/bin/python -m pytest -q

# Limpiar artefactos locales y el virtualenv (.venv)
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info