# Workstream D — Agentic SRE Log Intelligence Evaluation Suite

These evaluations use only the synthetic dataset in `sre-agent/logs/synthetic_logs.json`.
They prove three behaviors required by the challenge: grounded retrieval, operational diagnosis from retrieved evidence, and an explicit `I don't know` response when the evidence is absent.

## Run

```bash
python -m pip install -r sre-agent/requirements.txt
pytest -q sre-agent/tests
python sre-agent/app/sre_agent.py "Why did the last deploy fail?"
python sre-agent/app/sre_agent.py "Why was the embedding pod restarted?"
python sre-agent/app/sre_agent.py "What database caused the payment service outage?"
```

## D1 — Deployment failure is grounded

**Question**

```text
Why did the last deploy fail?
```

**Evidence that must be retrievable**

```text
2026-09-23T08:57:19Z deployment ERROR Deployment failed: readiness probe failed for pod embedding-service-7d8c9f6d7b-x2k4m
2026-09-23T08:57:20Z kubernetes WARNING Pod embedding-service-7d8c9f6d7b-x2k4m restarted because container exceeded memory limit
2026-09-23T08:58:02Z deployment INFO Deployment rolled back to devsecops-ai-service:7e21b8a
```

**Expected output**

```text
Based on the retrieved logs:
- ...readiness probe failed...
- ...exceeded memory limit...
- ...Deployment rolled back...

Conclusion: the deployment failed because the readiness probe failed. The affected pod also exceeded its memory limit and was restarted. The deployment was subsequently rolled back.
```

**Pass condition:** the answer cites/reproduces evidence from the synthetic logs and does not invent another cause.

**Screenshot placeholder:** `docs/screenshots/D1-grounded-answer.png`

## D2 — Pod restart is grounded

**Question**

```text
Why was the embedding pod restarted?
```

**Expected evidence**

```text
Pod embedding-service-7d8c9f6d7b-x2k4m restarted because container exceeded memory limit
```

**Expected conclusion**

```text
the embedding-service pod was restarted because the container exceeded its memory limit.
```

**Pass condition:** the memory-limit log line is present in the retrieved evidence.

**Screenshot placeholder:** `docs/screenshots/D2-memory-answer.png`

## D3 — Unknown question must not hallucinate

**Question**

```text
What database caused the payment service outage?
```

**Expected output**

```text
I don't know based on the available logs.
```

**Pass condition:** no database, payment outage, or unsupported root cause is invented.

**Screenshot placeholder:** `docs/screenshots/D3-unknown-answer.png`

## Why the grounding design matters

`all-MiniLM-L6-v2` is a small, local sentence-transformer model suitable for a simulated evaluation because it keeps embeddings local and inexpensive. ChromaDB stores the vectors and metadata locally. The agent then uses retrieved log text as its evidence boundary.

For an SRE assistant, grounding is more important than fluent free-form generation: an invented incident cause can send an engineer toward the wrong remediation. The explicit unknown path is therefore a safety property, not just a UX choice.

A production version should add authenticated log ingestion, source IDs/timestamps in every citation, tenant/namespace authorization, retention controls, prompt/input sanitization, rate limiting, audit logs, model/provider cost controls, and a production log store such as Loki.
