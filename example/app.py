import logging
import time
import os
from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry import metrics as otel_metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

# Ensure info logs are emitted so we can verify hooks installed
logging.basicConfig(level=logging.INFO)

# Configure tracing with Console exporter (avoids UDP size issues)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

# Configure OpenTelemetry metrics with Console exporter (default); if
# OTEL_EXPORTER_OTLP_ENDPOINT is set, also export OTLP to collector.
metric_readers = [
    PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=5000)
]
otel_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT") or os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT"
)
if otel_endpoint:
    metric_readers.append(
        PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otel_endpoint),
            export_interval_millis=5000,
        )
    )
resource = Resource.create(
    {"service.name": os.environ.get("OTEL_SERVICE_NAME", "gunicorn-app")}
)
otel_metrics.set_meter_provider(
    MeterProvider(metric_readers=metric_readers, resource=resource)
)

app = Flask(__name__)
app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)
FlaskInstrumentor().instrument_app(app)
GunicornInstrumentor().instrument()

# Application metrics using OpenTelemetry Metrics API (exported via Console and optional OTLP)
meter = otel_metrics.get_meter(__name__)
otel_request_counter = meter.create_counter(
    name="app.requests",
    description="Total application requests",
)
otel_request_duration = meter.create_histogram(
    name="app.request.duration",
    description="Application request duration",
    unit="s",
)


@app.route("/")
def root():
    start = time.time()
    try:
        otel_request_counter.add(1, {"http.target": "/"})
        return "ok"
    finally:
        duration = time.time() - start
        otel_request_duration.record(duration, {"http.target": "/"})


@app.route("/test")
def test():
    start = time.time()
    try:
        otel_request_counter.add(1, {"http.target": "/test"})
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("test_operation") as span:
            span.set_attribute("custom.key", "custom.value")
            return "done"
    finally:
        duration = time.time() - start
        otel_request_duration.record(duration, {"http.target": "/test"})
