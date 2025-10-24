import os
import time
import subprocess
import urllib.request
import urllib.parse
import json


# ANSI color codes for better visual output (darker, more readable)
class Colors:
    GREEN = "\033[32m"  # Dark green instead of bright green
    YELLOW = "\033[33m"  # Dark yellow instead of bright yellow
    RED = "\033[31m"  # Dark red instead of bright red
    BLUE = "\033[34m"  # Dark blue instead of bright blue
    CYAN = "\033[36m"  # Dark cyan instead of bright cyan
    MAGENTA = "\033[35m"  # Dark magenta for better variety
    BOLD = "\033[1m"
    END = "\033[0m"


def colorize(text: str, color: str) -> str:
    """Add ANSI color codes to text for better visual output."""
    return f"{color}{text}{Colors.END}"


def _prom_query(query: str) -> dict:
    url = f"http://localhost:9090/api/v1/query?query={urllib.parse.quote(query)}"
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_metrics_end_to_end():
    print(
        colorize(
            "🚀 Starting E2E test - bringing up Docker stack...",
            Colors.BOLD + Colors.BLUE,
        )
    )
    # Start stack
    cwd = os.path.join(os.path.dirname(__file__), "..", "e2e")
    print(colorize(f"📁 Working directory: {cwd}", Colors.BOLD + Colors.MAGENTA))
    print(
        colorize(
            "🐳 Running: docker compose -f compose.yaml up -d --build",
            Colors.BOLD + Colors.YELLOW,
        )
    )
    subprocess.run(
        ["docker", "compose", "-f", "compose.yaml", "up", "-d", "--build"],
        cwd=cwd,
        check=True,
    )
    print(colorize("✅ Docker stack started successfully", Colors.BOLD + Colors.GREEN))

    try:
        print(colorize("Warming up application...", Colors.YELLOW))
        # Warm up app - wait for Gunicorn to be ready
        for attempt in range(10):
            try:
                print(
                    colorize(
                        f"  Attempt {attempt + 1}/10: Testing endpoints...", Colors.CYAN
                    )
                )
                # Test both endpoints to ensure full application readiness
                urllib.request.urlopen("http://localhost:8000/", timeout=3).read()
                urllib.request.urlopen("http://localhost:8000/test", timeout=3).read()
                print(
                    colorize(
                        "  ✅ Application is responding", Colors.BOLD + Colors.GREEN
                    )
                )
                break
            except Exception as e:
                print(colorize(f"  Attempt {attempt + 1} failed: {e}", Colors.RED))
                if attempt < 9:  # Don't sleep on the last attempt
                    time.sleep(2)  # Increased delay for slower startup
        else:
            raise Exception("Application failed to start after 10 attempts")

        print(colorize("Waiting for Prometheus to scrape metrics...", Colors.YELLOW))
        time.sleep(15)  # Increased wait time for metrics to propagate
        print(colorize("⏳ Wait complete", Colors.BOLD + Colors.GREEN))

        print(colorize("Verifying metrics via Prometheus...", Colors.BLUE))

        # First, let's see what metrics are actually available
        print(colorize("  Checking available metrics...", Colors.CYAN))
        try:
            # Query for all metric names containing 'gunicorn'
            available_metrics = _prom_query('{__name__=~"gunicorn.*"}')
            if available_metrics.get("status") == "success":
                metric_names = []
                for result in available_metrics.get("data", {}).get("result", []):
                    metric_name = result.get("metric", {}).get("__name__", "")
                    if metric_name:
                        metric_names.append(metric_name)
                if metric_names:
                    print(
                        colorize(
                            f"  Available Gunicorn metrics: {', '.join(set(metric_names))}",
                            Colors.BLUE,
                        )
                    )
                else:
                    print(
                        colorize(
                            "  No Gunicorn metrics found in Prometheus", Colors.RED
                        )
                    )
            else:
                print(
                    colorize(
                        f"  Failed to query available metrics: {available_metrics}",
                        Colors.RED,
                    )
                )
        except Exception as e:
            print(colorize(f"  Error checking available metrics: {e}", Colors.RED))

        # Verify specific metrics exist via Prometheus (collector exposes Prometheus-style names)
        queries = [
            "gunicorn_requests_total",
            "gunicorn_request_duration_seconds_sum",
            "gunicorn_request_duration_seconds_count",
            "gunicorn_worker_cpu_percent",
            "gunicorn_worker_memory_rss_bytes",
        ]
        for q in queries:
            print(colorize(f"  Checking metric: {q}", Colors.CYAN))
            data = _prom_query(q)
            assert data.get("status") == "success", f"Query failed for {q}: {data}"
            assert data.get("data", {}).get("result"), f"no results for {q}"
            result_count = len(data.get("data", {}).get("result", []))
            print(
                colorize(
                    f"  Found {result_count} result(s) for {q}",
                    Colors.GREEN if result_count > 0 else Colors.RED,
                )
            )

        print(
            colorize(
                "🎉 All metrics verified successfully!", Colors.BOLD + Colors.GREEN
            )
        )

    finally:
        print(colorize("🧹 Cleaning up Docker stack...", Colors.BOLD + Colors.YELLOW))
        subprocess.run(
            ["docker", "compose", "-f", "compose.yaml", "down", "-v"], cwd=cwd
        )
        print(colorize("✅ Cleanup complete", Colors.BOLD + Colors.GREEN))
