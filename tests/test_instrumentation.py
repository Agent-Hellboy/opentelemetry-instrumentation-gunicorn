# Copyright The OpenTelemetry Authors
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

"""Tests for GunicornInstrumentor."""

import pytest
from unittest.mock import patch, MagicMock

from opentelemetry.instrumentation.gunicorn import GunicornInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


class TestGunicornInstrumentor:
    """Test suite for GunicornInstrumentor."""

    def setup_method(self):
        """Setup test fixtures."""
        self.tracer_provider = TracerProvider()
        self.exporter = InMemorySpanExporter()
        self.tracer_provider.add_span_processor(SimpleSpanProcessor(self.exporter))

    def test_instrument_creates_tracer(self):
        """Test that instrument creates a tracer."""
        instrumentor = GunicornInstrumentor()
        assert instrumentor._instrument is not None

    def test_instrumentation_dependencies(self):
        """Test instrumentation dependencies."""
        instrumentor = GunicornInstrumentor()
        deps = instrumentor.instrumentation_dependencies()
        assert isinstance(deps, tuple)
        assert any("gunicorn" in dep for dep in deps)

    def test_request_info_extraction_wsgi_environ(self):
        """Test extraction of request info from WSGI environ."""
        from opentelemetry.instrumentation.gunicorn import _extract_request_info

        environ = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/api/users",
            "REMOTE_ADDR": "127.0.0.1",
        }

        info = _extract_request_info((environ,))
        assert info["method"] == "GET"
        assert info["path"] == "/api/users"
        assert info["client"] == "127.0.0.1"

    def test_request_info_extraction_request_object(self):
        """Test extraction of request info from request object."""
        from opentelemetry.instrumentation.gunicorn import _extract_request_info

        request = MagicMock()
        request.method = "POST"
        request.path = "/api/data"

        info = _extract_request_info((request,))
        assert info["method"] == "POST"
        assert info["path"] == "/api/data"

    def test_request_info_extraction_unknown(self):
        """Test extraction with unknown request format."""
        from opentelemetry.instrumentation.gunicorn import _extract_request_info

        info = _extract_request_info(
            (
                None,
                "unknown",
            )
        )
        assert info["method"] == "UNKNOWN"
        assert info["path"] == "/"

    @patch(
        "opentelemetry.instrumentation.gunicorn.GunicornInstrumentor._instrument_hooks"
    )
    def test_instrument_success(self, mock_hooks):
        """Test successful instrumentation."""
        instrumentor = GunicornInstrumentor()
        instrumentor._instrument(tracer_provider=self.tracer_provider)
        mock_hooks.assert_called_once()

    def test_uninstrument(self):
        """Test uninstrumentation."""
        instrumentor = GunicornInstrumentor()
        # Should not raise any exception
        instrumentor._uninstrument()


if __name__ == "__main__":
    pytest.main([__file__])
