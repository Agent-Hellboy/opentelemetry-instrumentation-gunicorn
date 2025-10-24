# OpenTelemetry Instrumentation for Gunicorn

Automatic OpenTelemetry tracing and metrics for Gunicorn WSGI servers.

- Documentation: see docs site (mkdocs) or the `docs/` directory
- Quickstart: docs/quickstart.md
- Configuration: docs/configuration.md
- Implementation overview: docs/implementation.md

## Install

```bash
pip install opentelemetry-instrumentation-gunicorn opentelemetry-api opentelemetry-sdk
```

## Minimal Usage (Flask)

```python
from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

app = Flask(__name__)
GunicornInstrumentor().instrument()
```

For full examples and guidance, see the docs.
