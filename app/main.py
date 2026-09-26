"""Bytespoke assistant API."""

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest


app = FastAPI(title="Bytespoke Assistant", version="0.1.0")

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
    open_api_key="sk-proj-000000000000000000000000000000000000000000000000"
    print(f"OPENAI_API_KEY: {open_api_key}")
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
