from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


METRICS_FILE = Path("/app/mock-metrics.txt")


def load_metrics() -> str:
    """Load simulated metrics from the local metrics file."""
    values: dict[str, str] = {}

    for line in METRICS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        name, value = line.split(maxsplit=1)
        values[name] = value

    return f"""# HELP ci_pipeline_success_rate_percent CI pipeline success rate.
# TYPE ci_pipeline_success_rate_percent gauge
ci_pipeline_success_rate_percent {values["ci_pipeline_success_rate_percent"]}

# HELP pod_restart_count_15m Pod restarts in the last 15 minutes.
# TYPE pod_restart_count_15m gauge
pod_restart_count_15m {values["pod_restart_count_15m"]}

# HELP security_policy_denials_per_second Security policy denials per second.
# TYPE security_policy_denials_per_second gauge
security_policy_denials_per_second {values["security_policy_denials_per_second"]}

# HELP http_request_rate_per_second HTTP request rate.
# TYPE http_request_rate_per_second gauge
http_request_rate_per_second {values["http_request_rate_per_second"]}

# HELP http_5xx_rate_percent HTTP 5xx error rate.
# TYPE http_5xx_rate_percent gauge
http_5xx_rate_percent {values["http_5xx_rate_percent"]}

# HELP pod_availability_ready Number of ready pods.
# TYPE pod_availability_ready gauge
pod_availability_ready {values["pod_availability_ready"]}
"""


class MetricsHandler(BaseHTTPRequestHandler):
    """Serve simulated Prometheus metrics."""

    def do_GET(self) -> None:
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return

        data = load_metrics().encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain; version=0.0.4",
        )
        self.send_header(
            "Content-Length",
            str(len(data)),
        )
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        """Disable HTTP access logging."""
        return


if __name__ == "__main__":
    server = HTTPServer(
        ("0.0.0.0", 9100),
        MetricsHandler,
    )

    print(
        "Mock metrics exporter listening on "
        "http://0.0.0.0:9100/metrics"
    )

    server.serve_forever()