# Quickstart

## Install

```bash
pip install opentelemetry-instrumentation-gunicorn opentelemetry-api opentelemetry-sdk
# Exporters (choose one)
pip install opentelemetry-exporter-otlp
# or
pip install opentelemetry-exporter-jaeger
```

## Minimal app (Flask)

```python
# app.py
from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

app = Flask(__name__)
app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)
GunicornInstrumentor().instrument()

@app.route("/")
def hello():
    return "ok"
```

## Run

```bash
export OTEL_SERVICE_NAME=gunicorn-app
# Optional worker metrics
export OTEL_GUNICORN_TRACE_WORKERS=true

gunicorn app:app --workers 2
```

- Console exporter prints spans; for OTLP, set `OTEL_TRACES_EXPORTER=otlp` and `OTEL_EXPORTER_OTLP_ENDPOINT`.
- For a full example (Prometheus demo metrics, Console exporters), see `example_app/app.py`.
