import os
import time
import subprocess
import urllib.request
import urllib.parse
import json


def _prom_query(query: str) -> dict:
    url = f"http://localhost:9090/api/v1/query?query={urllib.parse.quote(query)}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_metrics_end_to_end():
    # Start stack
    cwd = os.path.join(os.path.dirname(__file__), "..", "e2e")
    subprocess.run(
        ["docker", "compose", "-f", "compose.yaml", "up", "-d", "--build"],
        cwd=cwd,
        check=True,
    )
    try:
        # Warm up app
        for _ in range(10):
            try:
                urllib.request.urlopen("http://localhost:8000/", timeout=2).read()
                urllib.request.urlopen("http://localhost:8000/test", timeout=2).read()
                break
            except Exception:
                time.sleep(1)

        # Wait for Prometheus to scrape
        time.sleep(8)

        # Verify metrics exist via Prometheus (collector exposes Prometheus-style names)
        queries = [
            "gunicorn_requests_total",
            "gunicorn_request_duration_seconds_sum",
            "gunicorn_request_duration_seconds_count",
            "gunicorn_worker_cpu_percent",
            "gunicorn_worker_memory_rss_bytes",
        ]
        for q in queries:
            data = _prom_query(q)
            assert data.get("status") == "success"
            assert data.get("data", {}).get("result"), f"no results for {q}"
    finally:
        subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "down", "-v"], cwd=cwd
        )
