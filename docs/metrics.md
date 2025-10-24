# Metrics

## Overview

The instrumentation automatically collects comprehensive metrics for monitoring Gunicorn performance and application health.

## Request Metrics

### Counter: `gunicorn.requests`

Tracks the total number of HTTP requests handled by Gunicorn workers.

**Attributes:**

- `http.method`: HTTP method (GET, POST, etc.)
- `http.target`: Request path
- `http.status_code`: HTTP response status code

### Histogram: `gunicorn.request.duration`

Measures the duration of HTTP requests in seconds.

**Attributes:**

- `http.method`: HTTP method
- `http.target`: Request path
- `http.status_code`: HTTP response status code

## Worker Metrics (when enabled)

!!! note "Worker metrics require environment variable"
Set `OTEL_GUNICORN_TRACE_WORKERS=true` to enable worker CPU and memory metrics.

### Gauge: `gunicorn.worker.cpu.percent`

Reports CPU usage percentage for each Gunicorn worker process.

**Attributes:**

- `worker.pid`: Process ID of the worker
- `worker.id`: Worker ID (0-based index)

### Gauge: `gunicorn.worker.memory.rss`

Reports Resident Set Size (RSS) memory usage in bytes for each worker.

**Attributes:**

- `worker.pid`: Process ID of the worker
- `worker.id`: Worker ID (0-based index)

## Prometheus Format Example

```
# HELP gunicorn_requests_total Total Gunicorn handled requests
# TYPE gunicorn_requests_total counter
gunicorn_requests_total{http_method="GET",http_target="/"} 42

# HELP gunicorn_request_duration_seconds Gunicorn request duration
# TYPE gunicorn_request_duration_seconds histogram
gunicorn_request_duration_seconds_bucket{http_method="GET",http_target="/",le="0.1"} 10
gunicorn_request_duration_seconds_bucket{http_method="GET",http_target="/",le="0.5"} 25
gunicorn_request_duration_seconds_bucket{http_method="GET",http_target="/",le="1.0"} 35
gunicorn_request_duration_seconds_bucket{http_method="GET",http_target="/",le="+Inf"} 42
gunicorn_request_duration_seconds_sum{http_method="GET",http_target="/"} 12.34
gunicorn_request_duration_seconds_count{http_method="GET",http_target="/"} 42

# HELP gunicorn_worker_cpu_percent Gunicorn worker CPU usage percentage
# TYPE gunicorn_worker_cpu_percent gauge
gunicorn_worker_cpu_percent{worker_pid="1234",worker_id="0"} 15.2

# HELP gunicorn_worker_memory_rss_bytes Gunicorn worker memory usage in bytes
# TYPE gunicorn_worker_memory_rss_bytes gauge
gunicorn_worker_memory_rss_bytes{worker_pid="1234",worker_id="0"} 52428800
```

## Configuration

Metrics are automatically collected when the instrumentation is enabled. Configure metric export using OpenTelemetry environment variables:

```bash
# Export to OTLP collector
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://localhost:4318/v1/metrics"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"

# Export to Prometheus (via collector)
export OTEL_METRICS_EXPORTER="prometheus"
```

## Viewing Metrics

Use tools like Prometheus, Grafana, or the OpenTelemetry Collector to collect and visualize these metrics.
