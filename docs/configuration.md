# Configuration

## Environment Variables

- `OTEL_SERVICE_NAME`: Service name (default: gunicorn-app)
- `OTEL_TRACES_EXPORTER`: Traces exporter (e.g., otlp)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP endpoint
- `OTEL_GUNICORN_TRACE_WORKERS`: Enable worker metrics collection (`true`/`false`)
- `OTEL_GUNICORN_CAPTURE_HEADERS`: Capture HTTP headers (`true`/`false`)

## Example

```bash
export OTEL_SERVICE_NAME=my-gunicorn-app
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_GUNICORN_TRACE_WORKERS=true
```
