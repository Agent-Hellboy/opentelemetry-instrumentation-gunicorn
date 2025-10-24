# OpenTelemetry Instrumentation for Gunicorn

[![PyPI version](https://badge.fury.io/py/opentelemetry-instrumentation-gunicorn.svg)](https://pypi.org/project/opentelemetry-instrumentation-gunicorn/)
[![Python versions](https://img.shields.io/pypi/pyversions/opentelemetry-instrumentation-gunicorn.svg)](https://pypi.org/project/opentelemetry-instrumentation-gunicorn/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://agent-hellboy.github.io/opentelemetry-instrumentation-gunicorn/)
[![CI](https://github.com/Agent-Hellboy/opentelemetry-instrumentation-gunicorn/actions/workflows/ci.yml/badge.svg)](https://github.com/Agent-Hellboy/opentelemetry-instrumentation-gunicorn/actions/workflows/ci.yml)

Automatic OpenTelemetry tracing and metrics for Gunicorn WSGI servers.

- **Documentation**: [https://agent-hellboy.github.io/opentelemetry-instrumentation-gunicorn/](https://agent-hellboy.github.io/opentelemetry-instrumentation-gunicorn/)
- **Quickstart**: [Quickstart Guide](https://agent-hellboy.github.io/opentelemetry-instrumentation-gunicorn/quickstart/)
- **Installation**: [Installation Guide](https://agent-hellboy.github.io/opentelemetry-instrumentation-gunicorn/installation/)
- **Configuration**: [Configuration Guide](https://agent-hellboy.github.io/opentelemetry-instrumentation-gunicorn/configuration/)

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
