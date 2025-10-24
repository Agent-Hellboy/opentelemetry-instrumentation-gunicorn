# Using with Django

## Django Settings

Add to your `settings.py`:

```python
# settings.py
INSTALLED_APPS = [
    # ... your apps
]

# OpenTelemetry configuration
OPENTELEMETRY = {
    'TRACE': {
        'ENABLED': True,
        'EXPORTER': 'console',  # or 'otlp', 'jaeger'
    },
    'METRICS': {
        'ENABLED': True,
        'EXPORTER': 'console',  # or 'otlp'
    }
}
```

## WSGI Application

Create `wsgi.py` with instrumentation:

```python
import os
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

set_meter_provider(MeterProvider(
    metric_readers=[
        PeriodicExportingMetricReader(
            exporter=ConsoleMetricExporter(),
            export_interval_millis=10000
        )
    ]
))

# Instrument Gunicorn BEFORE importing Django application
GunicornInstrumentor().instrument()

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
wsgi_module = "your_project.wsgi:application"
accesslog = "logs/access.log"
errorlog = "logs/error.log"
```

## Running with Django

```bash
# Run with Gunicorn
gunicorn --config gunicorn.conf.py your_project.wsgi:application

# Or using the wsgi module directly
gunicorn --config gunicorn.conf.py wsgi:application
```

## Environment Variables

```bash
# Enable worker metrics
export OTEL_GUNICORN_TRACE_WORKERS=true

# Django settings
export DJANGO_SETTINGS_MODULE=your_project.settings

# OpenTelemetry configuration
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://localhost:4318/v1/metrics"
export OTEL_METRICS_EXPORTER="otlp"
export OTEL_TRACES_EXPORTER="console"
```

## Management Command (Optional)

Create a management command for easier instrumentation setup:

```python
# your_app/management/commands/instrument.py
from django.core.management.base import BaseCommand
from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

class Command(BaseCommand):
    help = 'Instrument Gunicorn with OpenTelemetry'

    def handle(self, *args, **options):
        GunicornInstrumentor().instrument()
        self.stdout.write(
            self.style.SUCCESS('Gunicorn instrumentation enabled')
        )
```
