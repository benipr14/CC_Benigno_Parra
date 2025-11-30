FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime and test dependencies (we reuse requirements-dev for reproducibility)
COPY requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . /app

# Expose the port the app uses internally
EXPOSE 8000

# Default command: run uvicorn serving the FastAPI app
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
