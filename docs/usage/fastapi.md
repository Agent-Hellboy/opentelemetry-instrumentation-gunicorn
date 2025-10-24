# Using with FastAPI

## Basic Setup

```python
from fastapi import FastAPI
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Initialize OpenTelemetry BEFORE creating FastAPI app
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Instrument Gunicorn
GunicornInstrumentor().instrument()

# Create FastAPI app
app = FastAPI(title="My FastAPI App")

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

## Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"  # Use Uvicorn worker for async
accesslog = "logs/access.log"
errorlog = "logs/error.log"
```

## Running the Application

```bash
# Install uvicorn workers
pip install uvicorn[standard]

# Run with Gunicorn
gunicorn --config gunicorn.conf.py main:app
```

## With Metrics Export

```python
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry import trace, metrics
from fastapi import FastAPI

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

# Create FastAPI app
app = FastAPI()

# ... your routes
```

## ASGI vs WSGI

For FastAPI applications, you have two options:

### Option 1: ASGI with Uvicorn Workers (Recommended)

```python
# gunicorn.conf.py
worker_class = "uvicorn.workers.UvicornWorker"
workers = 4
bind = "0.0.0.0:8000"
```

### Option 2: WSGI with Standard Workers

```python
# main.py - Convert FastAPI to WSGI
from fastapi import FastAPI
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

GunicornInstrumentor().instrument()

app = FastAPI()

# ... routes ...

# Convert to WSGI
from fastapi.middleware.wsgi import WSGIMiddleware
wsgi_app = WSGIMiddleware(app)
```

```python
# gunicorn.conf.py
worker_class = "sync"
workers = 4
bind = "0.0.0.0:8000"
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

# For ASGI mode
export WEB_CONCURRENCY=4
```

## Middleware Integration

FastAPI works well with OpenTelemetry middleware:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace

app = FastAPI()

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(f"fastapi.{request.method}.{request.url.path}"):
            response = await call_next(request)
            return response

app.add_middleware(TracingMiddleware)
```
