# Troubleshooting

- Spans not visible:
  - Ensure exporter configured and backend reachable
  - Set `OTEL_LOG_LEVEL=debug`
- Large UDP errors with Jaeger Thrift:
  - Use Console or OTLP exporters
- High memory/CPU:
  - Reduce batch processor queue size
  - Disable header capture (`OTEL_GUNICORN_CAPTURE_HEADERS=false`)
  - Disable worker metrics (`OTEL_GUNICORN_TRACE_WORKERS=false`)
