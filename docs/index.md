# OpenTelemetry Gunicorn Instrumentation

[![PyPI version](https://badge.fury.io/py/opentelemetry-instrumentation-gunicorn.svg)](https://pypi.org/project/opentelemetry-instrumentation-gunicorn/)
[![Python versions](https://img.shields.io/pypi/pyversions/opentelemetry-instrumentation-gunicorn.svg)](https://pypi.org/project/opentelemetry-instrumentation-gunicorn/)

**Automatic OpenTelemetry tracing and metrics for Gunicorn WSGI servers.**

Gunicorn is a popular Python WSGI HTTP server that powers many production applications. This instrumentation provides comprehensive observability by automatically collecting traces and metrics from your Gunicorn workers, giving you insights into request performance, worker health, and application behavior.

## Key Features

- **Automatic Tracing**: Request tracing with distributed context propagation
- **Rich Metrics**: Request counts, duration histograms, and worker resource usage
- **Zero Configuration**: Drop-in instrumentation with sensible defaults
- **Framework Agnostic**: Works with Flask, Django, FastAPI, and any WSGI app


## Quick Start

### Installation

```bash
pip install opentelemetry-instrumentation-gunicorn
```

### Basic Usage

```python
from flask import Flask
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

app = Flask(__name__)

# Instrument Gunicorn (before running)
GunicornInstrumentor().instrument()

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

### Run with Gunicorn

```bash
# Basic configuration
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app

# With OTLP export
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
export OTEL_SERVICE_NAME="my-gunicorn-app"
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

## Metrics Collected

| Metric | Type | Description |
|--------|------|-------------|
| `gunicorn.requests` | Counter | Total HTTP requests handled |
| `gunicorn.request.duration` | Histogram | Request processing duration |
| `gunicorn.worker.cpu.percent` | Gauge | Worker CPU usage percentage |
| `gunicorn.worker.memory.rss` | Gauge | Worker memory usage in bytes |

## Framework Integrations

### Flask
```python
from flask import Flask
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

app = Flask(__name__)
GunicornInstrumentor().instrument()

# Your Flask routes...
```

### Django
```python
# wsgi.py
import os
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
GunicornInstrumentor().instrument()  # Before Django import

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### FastAPI
```python
from fastapi import FastAPI
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

GunicornInstrumentor().instrument()  # Before FastAPI app creation

app = FastAPI()

# Your FastAPI routes...
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_SERVICE_NAME` | Service name for telemetry | `unknown_service` |
| `OTEL_GUNICORN_TRACE_WORKERS` | Enable worker metrics | `false` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | - |
| `OTEL_TRACES_EXPORTER` | Trace exporter | `console` |
| `OTEL_METRICS_EXPORTER` | Metrics exporter | `console` |

### Advanced Configuration

```python
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

# Custom configuration
instrumentor = GunicornInstrumentor()
instrumentor.instrument(
    # Custom options can be passed here
)
```

## Documentation

- **[Quickstart](quickstart.md)**: Get up and running in 5 minutes
- **[Configuration](configuration.md)**: Detailed configuration options
- **[Usage Examples](usage/)**: Framework-specific integration guides
- **[Metrics](metrics.md)**: Complete metrics reference
- **[API Reference](api.md)**: Developer API documentation
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Contributing

We welcome contributions! See our [contributing guide](contributing.md) for development setup and guidelines.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.
