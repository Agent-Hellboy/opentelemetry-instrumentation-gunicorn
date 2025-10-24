# Copyright Prince Roshan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
OpenTelemetry instrumentation for Gunicorn WSGI server.

This module provides automatic instrumentation for Gunicorn applications,
enabling comprehensive tracing of HTTP requests and worker metrics.

Usage:
------

    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor

    # Setup tracing
    jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

    # Instrument Gunicorn
    GunicornInstrumentor().instrument()

Environment Variables:
---------------------
    OTEL_GUNICORN_TRACE_WORKERS: Enable worker trace metrics (default: false)
    OTEL_GUNICORN_CAPTURE_HEADERS: Capture HTTP headers (default: true)
"""

import logging
import os
import time
from typing import Any, Callable
from collections.abc import Iterable

import psutil

try:
    from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
except Exception:  # pragma: no cover - fallback for older versions
    from opentelemetry.instrumentation.instrumentation import BaseInstrumentor
from opentelemetry.trace import Tracer, get_tracer
from opentelemetry.trace import Status, StatusCode
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
    get_meter,
)

# Lazily initialized metric handles (OpenTelemetry Metrics API)
_METER = None
_REQUEST_COUNTER = None  # Counter
_REQUEST_DURATION = None  # Histogram
_WORKER_CPU_GAUGE = None  # ObservableGauge for worker CPU
_WORKER_MEMORY_GAUGE = None  # ObservableGauge for worker memory


def _init_otel_metrics() -> None:
    """Initialize OTEL metric instruments (idempotent)."""
    global \
        _METER, \
        _REQUEST_COUNTER, \
        _REQUEST_DURATION, \
        _WORKER_CPU_GAUGE, \
        _WORKER_MEMORY_GAUGE
    if _METER is None:
        _METER = get_meter(__name__, __version__)

    if _REQUEST_COUNTER is None:
        _REQUEST_COUNTER = _METER.create_counter(
            name="gunicorn.requests",
            description="Total Gunicorn handled requests",
            unit="1",
        )

    if _REQUEST_DURATION is None:
        _REQUEST_DURATION = _METER.create_histogram(
            name="gunicorn.request.duration",
            description="Gunicorn request duration",
            unit="s",
        )

    if _WORKER_CPU_GAUGE is None:
        _WORKER_CPU_GAUGE = _METER.create_observable_gauge(
            name="gunicorn.worker.cpu.percent",
            callbacks=[_observe_worker_cpu],
            description="Gunicorn worker CPU usage percent",
            unit="percent",
        )

    if _WORKER_MEMORY_GAUGE is None:
        _WORKER_MEMORY_GAUGE = _METER.create_observable_gauge(
            name="gunicorn.worker.memory.rss",
            callbacks=[_observe_worker_memory],
            description="Gunicorn worker memory RSS in bytes",
            unit="By",
        )


logger = logging.getLogger(__name__)

__version__ = "0.1.0b0"
__all__ = ["GunicornInstrumentor"]


class GunicornInstrumentor(BaseInstrumentor):
    """OpenTelemetry instrumentation for Gunicorn WSGI server."""

    def instrumentation_dependencies(self) -> tuple[str, ...]:
        """Return list of packages this instrumentation requires."""
        return ("gunicorn >= 21.0.0",)

    def _instrument(self, **kwargs: Any) -> None:
        """Instrument Gunicorn workers and master process."""
        tracer_provider = kwargs.get("tracer_provider")

        self._tracer = get_tracer(
            __name__,
            __version__,
            tracer_provider=tracer_provider,
            schema_url="https://opentelemetry.io/schemas/1.14.0",
        )

        # Initialize OpenTelemetry metrics
        _init_otel_metrics()

        # Create instrumentation hooks
        self._instrument_hooks()

    def _uninstrument(self, **kwargs: Any) -> None:
        """Remove instrumentation."""
        logger.debug("Uninstrumenting Gunicorn")

    def _instrument_hooks(self) -> None:
        """Setup instrumentation hooks for Gunicorn lifecycle events."""
        try:
            # Instrument worker initialization
            _wrap_worker_init(self._tracer)

            # Instrument request handling
            _wrap_request_handling(self._tracer)

            # Instrument worker metrics collection (via background thread from worker init)
            logger.info("Gunicorn instrumentation hooks installed")

        except Exception as e:
            logger.warning("Failed to instrument Gunicorn: %s", e)


def _wrap_worker_init(tracer: Tracer) -> None:
    """Wrap worker initialization to track startup spans."""
    from gunicorn.workers import base

    original_init = base.Worker.__init__

    def wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
        with tracer.start_as_current_span("gunicorn.worker.init") as span:
            span.set_attribute("process.pid", os.getpid())
            span.set_attribute("process.executable.name", "gunicorn-worker")
            span.set_attribute("worker.age", getattr(self, "age", 0))

            result = original_init(self, *args, **kwargs)

            worker_id = str(getattr(self, "worker_id", "unknown"))
            span.set_attribute("worker.id", worker_id)

            # Start background metrics collector if enabled
            if os.environ.get("OTEL_GUNICORN_TRACE_WORKERS", "false").lower() == "true":
                try:
                    _start_worker_metrics_collector(worker_id)
                except Exception as e:  # pragma: no cover
                    logger.debug("Failed to start worker metrics collector: %s", e)

            return result

    base.Worker.__init__ = wrapped_init
    logger.debug("Wrapped Worker.__init__")


def _observe_worker_cpu(options: CallbackOptions) -> Iterable[Observation]:
    """Observe CPU usage for all Gunicorn worker processes."""
    if os.environ.get("OTEL_GUNICORN_TRACE_WORKERS", "false").lower() != "true":
        return

    try:
        # Find all gunicorn worker processes
        found_workers = False
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if (
                    proc.info["name"] == "python"
                    and proc.info["cmdline"]
                    and "gunicorn" in " ".join(proc.info["cmdline"])
                ):
                    cpu = proc.cpu_percent(interval=None)
                    found_workers = True
                    yield Observation(
                        cpu,
                        {
                            "process.pid": str(proc.pid),
                            "gunicorn.worker.id": "worker",  # Simplified worker ID
                        },
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if not found_workers:
            # If no workers found, yield a default observation for current process
            try:
                cpu = psutil.Process().cpu_percent(interval=None)
                yield Observation(
                    cpu,
                    {"process.pid": str(os.getpid()), "gunicorn.worker.id": "current"},
                )
            except Exception:
                yield Observation(
                    0.0, {"process.pid": "unknown", "gunicorn.worker.id": "unknown"}
                )
    except Exception:
        # If we can't observe workers, yield a default observation
        yield Observation(
            0.0, {"process.pid": "unknown", "gunicorn.worker.id": "unknown"}
        )


def _observe_worker_memory(options: CallbackOptions) -> Iterable[Observation]:
    """Observe memory usage for all Gunicorn worker processes."""
    if os.environ.get("OTEL_GUNICORN_TRACE_WORKERS", "false").lower() != "true":
        return

    try:
        # Find all gunicorn worker processes
        found_workers = False
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if (
                    proc.info["name"] == "python"
                    and proc.info["cmdline"]
                    and "gunicorn" in " ".join(proc.info["cmdline"])
                ):
                    rss = proc.memory_info().rss
                    found_workers = True
                    yield Observation(
                        rss,
                        {
                            "process.pid": str(proc.pid),
                            "gunicorn.worker.id": "worker",  # Simplified worker ID
                        },
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if not found_workers:
            # If no workers found, yield a default observation for current process
            try:
                rss = psutil.Process().memory_info().rss
                yield Observation(
                    rss,
                    {"process.pid": str(os.getpid()), "gunicorn.worker.id": "current"},
                )
            except Exception:
                yield Observation(
                    0, {"process.pid": "unknown", "gunicorn.worker.id": "unknown"}
                )
    except Exception:
        # If we can't observe workers, yield a default observation
        yield Observation(
            0, {"process.pid": "unknown", "gunicorn.worker.id": "unknown"}
        )


def _start_worker_metrics_collector(worker_id: str) -> None:
    """Worker metrics are now registered globally, just log that worker tracing is enabled."""
    logger.debug("Worker metrics collection enabled for worker %s", worker_id)


def _wrap_request_handling(tracer: Tracer) -> None:
    """Wrap request handling in workers to create request spans."""
    from gunicorn.workers import sync, gthread

    def _wrap_handle_request(original_handle: Callable) -> Callable:
        """Create wrapper for request handling methods."""

        def wrapped_handle(self: Any, *args: Any, **kwargs: Any) -> Any:
            request_start = time.time()

            # Extract request info from arguments
            request_info = _extract_request_info(args)
            method = request_info.get("method", "UNKNOWN")
            path = request_info.get("path", "/")
            worker_id = str(getattr(self, "worker_id", "unknown"))

            span_name = f"gunicorn.request.{method.lower()}"

            with tracer.start_as_current_span(span_name) as span:
                # Set HTTP attributes (using strings for compatibility)
                span.set_attribute("http.method", method)
                span.set_attribute("http.url.path", path)
                span.set_attribute("worker.pid", os.getpid())
                span.set_attribute("worker.id", worker_id)

                try:
                    result = original_handle(self, *args, **kwargs)
                    duration = time.time() - request_start
                    span.set_attribute(
                        "gunicorn.request.duration_ms", int(duration * 1000)
                    )

                    # Record OTEL metrics
                    if _REQUEST_COUNTER is not None:
                        try:
                            _REQUEST_COUNTER.add(
                                1,
                                {
                                    "http.method": method,
                                    "http.target": path,
                                    "gunicorn.worker.id": worker_id,
                                },
                            )
                        except Exception:
                            pass
                    if _REQUEST_DURATION is not None:
                        try:
                            _REQUEST_DURATION.record(
                                duration,
                                {
                                    "http.method": method,
                                    "http.target": path,
                                    "gunicorn.worker.id": worker_id,
                                },
                            )
                        except Exception:
                            pass

                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR))
                    # Count error requests as well
                    if _REQUEST_COUNTER is not None:
                        try:
                            _REQUEST_COUNTER.add(
                                1,
                                {
                                    "http.method": method,
                                    "http.target": path,
                                    "gunicorn.worker.id": worker_id,
                                    "error": True,
                                },
                            )
                        except Exception:
                            pass
                    raise

        return wrapped_handle

    # Wrap sync worker handle_request
    if hasattr(sync.SyncWorker, "handle_request"):
        sync.SyncWorker.handle_request = _wrap_handle_request(
            sync.SyncWorker.handle_request
        )
        logger.debug("Wrapped SyncWorker.handle_request")

    # Wrap thread worker handle_request
    if hasattr(gthread.ThreadWorker, "handle_request"):
        gthread.ThreadWorker.handle_request = _wrap_handle_request(
            gthread.ThreadWorker.handle_request
        )
        logger.debug("Wrapped ThreadWorker.handle_request")


def _instrument_worker_metrics(tracer: Tracer) -> None:
    """Instrument worker metrics collection using metrics API."""
    # TODO: Implement metrics instrumentation
    # This will use OpenTelemetry Metrics API to export:
    # - Worker CPU usage
    # - Worker memory usage
    # - Request latency histograms
    # - Error rates
    logger.debug("Worker metrics instrumentation enabled")


def _extract_request_info(args: tuple[Any, ...]) -> dict:
    """Extract HTTP request information from worker method arguments.

    Args:
        args: Method arguments tuple

    Returns:
        Dictionary with request method, path, and client info
    """
    request_info = {
        "method": "UNKNOWN",
        "path": "/",
        "client": None,
    }

    for arg in args:
        if arg is None:
            continue

        # Handle WSGI environ dict
        if isinstance(arg, dict) and "REQUEST_METHOD" in arg:
            request_info["method"] = arg.get("REQUEST_METHOD", "UNKNOWN")
            request_info["path"] = arg.get("PATH_INFO", "/")
            request_info["client"] = arg.get("REMOTE_ADDR", "unknown")
            break

        # Handle request objects with method/path attributes
        if hasattr(arg, "method") and hasattr(arg, "path"):
            request_info["method"] = str(getattr(arg, "method", "UNKNOWN"))
            request_info["path"] = str(getattr(arg, "path", "/"))
            break

    return request_info
