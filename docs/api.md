# API Reference

## GunicornInstrumentor

The main instrumentation class for Gunicorn.

```python
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
```

### Methods

#### `instrument()`
Instruments Gunicorn to collect traces and metrics.

```python
GunicornInstrumentor().instrument()
```

**Returns:** `None`

**Raises:** `Exception` if instrumentation fails

#### `uninstrument()`
Removes Gunicorn instrumentation.

```python
GunicornInstrumentor().uninstrument()
```

**Returns:** `None`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_GUNICORN_TRACE_WORKERS` | Enable worker CPU/memory metrics | `false` |
| `OTEL_SERVICE_NAME` | Service name for telemetry | `unknown_service` |
| `OTEL_TRACES_EXPORTER` | Trace exporter (`console`, `otlp`, `jaeger`) | `console` |
| `OTEL_METRICS_EXPORTER` | Metrics exporter (`console`, `otlp`) | `console` |

### OTLP Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint | `http://localhost:4318` |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` | Metrics-specific OTLP endpoint | Uses `OTEL_EXPORTER_OTLP_ENDPOINT` |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | Protocol (`grpc`, `http/protobuf`) | `grpc` |

### Jaeger Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OTEL_EXPORTER_JAEGER_ENDPOINT` | Jaeger collector endpoint | `http://localhost:14268/api/traces` |
| `OTEL_EXPORTER_JAEGER_USER` | Basic auth username | - |
| `OTEL_EXPORTER_JAEGER_PASSWORD` | Basic auth password | - |

## Metrics

### Request Metrics

#### `gunicorn.requests` (Counter)
- **Type:** Counter
- **Description:** Total number of HTTP requests
- **Attributes:**
  - `http.method`: HTTP method
  - `http.target`: Request path
  - `http.status_code`: Response status code

#### `gunicorn.request.duration` (Histogram)
- **Type:** Histogram
- **Description:** Request duration in seconds
- **Attributes:**
  - `http.method`: HTTP method
  - `http.target`: Request path
  - `http.status_code`: Response status code

### Worker Metrics

#### `gunicorn.worker.cpu.percent` (Gauge)
- **Type:** Observable Gauge
- **Description:** Worker CPU usage percentage
- **Attributes:**
  - `worker.pid`: Process ID
  - `worker.id`: Worker ID

#### `gunicorn.worker.memory.rss` (Gauge)
- **Type:** Observable Gauge
- **Description:** Worker memory usage in bytes
- **Attributes:**
  - `worker.pid`: Process ID
  - `worker.id`: Worker ID

## Tracing

### Spans

The instrumentation creates spans for:

- **Request processing:** `gunicorn.request`
  - Attributes: `http.method`, `http.target`, `http.status_code`
  - Events: Request start/completion

- **Worker lifecycle:** `gunicorn.worker`
  - Attributes: `worker.pid`, `worker.id`
  - Events: Worker start/shutdown

## Examples

### Basic Instrumentation

```python
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

# Instrument Gunicorn
instrumentor = GunicornInstrumentor()
instrumentor.instrument()

# Your WSGI app...
```

### Custom Configuration

```python
import os
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider

# Set environment variables
os.environ['OTEL_SERVICE_NAME'] = 'my-gunicorn-app'
os.environ['OTEL_GUNICORN_TRACE_WORKERS'] = 'true'

# Configure providers
# ... setup TracerProvider and MeterProvider ...

# Instrument
GunicornInstrumentor().instrument()
```

### Cleanup

```python
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

instrumentor = GunicornInstrumentor()
instrumentor.uninstrument()  # Remove instrumentation
```
