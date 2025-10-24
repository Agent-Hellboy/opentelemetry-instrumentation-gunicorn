# Using with Flask

## Basic Setup

```python
from flask import Flask
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Instrument Gunicorn
GunicornInstrumentor().instrument()

# Create Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

## Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
accesslog = "logs/access.log"
errorlog = "logs/error.log"
```

## Running the Application

```bash
# Run with Gunicorn
gunicorn --config gunicorn.conf.py app:app
```

## With Metrics Export

```python
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry import trace, metrics

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Initialize metrics
set_meter_provider(MeterProvider(
    metric_readers=[
        PeriodicExportingMetricReader(
            exporter=ConsoleMetricExporter(),
            export_interval_millis=10000
        )
    ]
))

# Instrument Gunicorn
GunicornInstrumentor().instrument()

# Flask app...
```

## Environment Variables

```bash
# Enable worker metrics
export OTEL_GUNICORN_TRACE_WORKERS=true

# Configure metrics export
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://localhost:4318/v1/metrics"
export OTEL_METRICS_EXPORTER="otlp"

# Configure tracing
export OTEL_TRACES_EXPORTER="console"
```
