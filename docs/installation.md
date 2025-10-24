# Installation

## Requirements

- Python 3.10+
- Gunicorn 21.0.0+

## Install Package

```bash
pip install opentelemetry-instrumentation-gunicorn
```

## Install with Extras

```bash
# With OTLP exporter for metrics
pip install opentelemetry-instrumentation-gunicorn opentelemetry-exporter-otlp

# With Jaeger exporter for traces
pip install opentelemetry-instrumentation-gunicorn opentelemetry-exporter-jaeger

# For development and testing
pip install opentelemetry-instrumentation-gunicorn[test]
pip install opentelemetry-instrumentation-gunicorn[docs]

# For development with linting and formatting tools
pip install opentelemetry-instrumentation-gunicorn[dev]
```

## Verify Installation

```bash
python -c "import opentelemetry.instrumentation.gunicorn; print('Installation successful!')"
```
