"""
Simple OpenTelemetry initialization helper.

Usage:
  - Set environment variables: OTEL_EXPORTER_OTLP_ENDPOINT and OTEL_API_KEY
  - Import and call `init_tracing("service-name")` early in app startup.

This file is a minimal, optional helper. It requires opentelemetry packages:
  pip install opentelemetry-sdk opentelemetry-exporter-otlp

Do not import this module unless you have set the required env vars.
"""
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
except Exception:  # pragma: no cover - import error handled at runtime
    OTLPSpanExporter = None


def init_tracing(service_name: str = "cc-app") -> Optional[TracerProvider]:
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    api_key = os.getenv("OTEL_API_KEY")
    if not endpoint or not api_key:
        return None
    if OTLPSpanExporter is None:
        raise RuntimeError("OTLP exporter not installed. Run 'pip install opentelemetry-exporter-otlp'")

    headers = ("Authorization", f"Bearer {api_key}")
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=(headers,))

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return provider
