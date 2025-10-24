FROM python:3.12-slim

WORKDIR /app
COPY ../.. /app

RUN pip install --no-cache-dir . flask opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-flask opentelemetry-instrumentation-wsgi gunicorn opentelemetry-exporter-otlp-proto-http

ENV OTEL_SERVICE_NAME=gunicorn-app

EXPOSE 8000

CMD ["gunicorn", "-c", "example/gunicorn.conf.py", "example.app:app"]
