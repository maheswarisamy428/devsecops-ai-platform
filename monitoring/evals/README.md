# Monitoring evaluation fixtures

Copy one fixture over `monitoring/mock-metrics.txt` and start the local stack:

```bash
cp monitoring/evals/normal-metrics.txt monitoring/mock-metrics.txt
docker compose -f monitoring/docker-compose.yml up
```

Then repeat with either incident fixture. The dashboard is a Grafana JSON definition and the exporter exposes the fixture values as Prometheus gauges.

The evaluation is intentionally simulated: changing the fixture is not the same as observing a real Kubernetes restart or Kyverno event. The scenario demonstrates how the dashboard and alert rules are expected to respond to those signals.
