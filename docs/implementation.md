# Implementation Overview

- Instrumentor wraps:
  - `gunicorn.workers.base.Worker.__init__` → span `gunicorn.worker.init`
  - `SyncWorker.handle_request` / `ThreadWorker.handle_request` → span `gunicorn.request.{method}`
- Span attributes:
  - HTTP: `http.method`, `http.url.path`, `http.status_code`
  - Worker: `worker.pid`, `worker.id`
- Metrics (OpenTelemetry Metrics API):
  - Counter: `gunicorn.requests`
  - Histogram: `gunicorn.request.duration` (seconds)
  - ObservableGauges: `gunicorn.worker.cpu.percent`, `gunicorn.worker.memory.rss`
- Enable worker gauges with `OTEL_GUNICORN_TRACE_WORKERS=true`.

Example span (request):

```yaml
name: gunicorn.request.get
attributes:
  http.method: GET
  http.url.path: /
  worker.pid: 12345
  worker.id: worker_0
```

See full details previously in IMPLEMENTATION.md; this page is the concise reference.
