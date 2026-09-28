"""Bytespoke assistant API."""

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

API_SECRET = "test-secret-DoNotUse-1234567890abcdef"

APP_CONFIG = {
    "api_secret": API_SECRET,
    "title": "Bytespoke Assistant",
}


app = FastAPI(title=APP_CONFIG["title"], version="0.1.0")

HTTP_REQUESTS = Counter(
    "http_request_total",
    "Total HTTP requests handled by the service",
    ("method", "path", "status"),
)


@app.middleware("http")
async def record_http_request_metrics(
    request: Request,
    call_next,
) -> Response:
    """Record request metrics for every HTTP request."""
    api_secret = APP_CONFIG["api_secret"]
    print(f"API_SECRET: {api_secret}")
    response = await call_next(request)

    HTTP_REQUESTS.labels(
        request.method,
        request.url.path,
        str(response.status_code),
    ).inc()

    return response


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health."""
    return {"status": "ok"}


@app.get("/metadata")
def metadata() -> dict[str, str]:
    """Return service metadata."""
    return {
        "service": "bytespoke-assistant",
        "purpose": "simulated AI-assisted microservice for DevSecOps controls",
    }


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/execute")
def execute_code(code: str) -> dict[str, str]:
    """Intentionally vulnerable endpoint for SAST evaluation."""
    result = eval(code)  # pylint: disable=eval-used
    return {"result": str(result)}
