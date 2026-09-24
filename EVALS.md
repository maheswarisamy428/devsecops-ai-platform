# Simulated Evaluation Suite

This document is the evidence map for the challenge. Every scenario has a **stimulus**, **control**, **expected outcome**, and **evidence to capture**. The fixtures are deliberately negative and must not be deployed.

## Evidence convention

- **Expected:** behavior the design must produce.
- **Observed:** placeholder until the candidate runs the command locally/CI.
**Evidence:** uploaded under `docs/screenshots/`
- No statement below should be interpreted as proof of a live Azure or Kubernetes deployment.

---

# A — Secure CI/CD Pipeline

Pipeline order:

`quality -> SAST/SCA/secret -> IaC -> build -> Trivy -> Kubernetes policy evaluation`

The early checks are cheap and source-oriented. The image scan happens only after an image exists. Kubernetes policy checks happen after the artifact is built because they validate the deployment layer.

| ID | Scenario | Expected stage | Expected result | Why it is blocked there |
|---|---|---|---|---|
| A1 | Known-vulnerable Python dependency introduced | pip-audit | **FAIL** | Dependency advisories are the most direct signal; waiting for image scanning is slower and less specific. |
| A2 | API key committed to repository | Gitleaks | **FAIL** | Secrets must be stopped before build/deploy; later stages cannot reliably erase git history. |
| A3 | Dockerfile uses `FROM python:latest` | Semgrep Dockerfile rule | **FAIL** | Mutable base tags create non-reproducible builds; source policy is the earliest and clearest control. |
| A4 | Clean PR and pinned base image | All applicable gates | **PASS** | No known finding is introduced; the artifact can proceed to build and Trivy. |
| A5 | Image contains HIGH/CRITICAL vulnerability | Trivy | **FAIL** | The image is the deployable artifact, so the final artifact gate blocks promotion. |

### A1 — vulnerable dependency

Fixture: `evals/workstream-a/vulnerable-requirements.txt`

Command:

```bash
pip-audit -r evals/workstream-a/vulnerable-requirements.txt
```

Expected trace:

```text
Found 1 known vulnerability in the evaluation dependency set
ERROR: pip-audit exited with status 1
```

The exact CVE/advisory identifier should be copied from the tool output used during the final evidence run because the public advisory database changes over time.

**Evidence:** uploaded under `docs/screenshots/workstream-A/`

### A2 — hardcoded secret

Fixture: `evals/workstream-a/hardcoded-secret.txt`

Command:

```bash
gitleaks dir evals/workstream-a/hardcoded-secret.txt --no-banner
```

Expected trace:

```text
Finding: hardcoded credential / API-key-like value
Exit code: 1
```

The test value is intentionally fake. Never replace it with a real credential.

**Evidence:** uploaded under `docs/screenshots/workstream-A/`

### A3 — mutable `latest` image tag

Fixture: `evals/workstream-a/Dockerfile.latest`

Command:

```bash
semgrep scan --config security/semgrep.yml evals/workstream-a/Dockerfile.latest --error
```

Expected trace:

```text
docker-no-latest-tag
ERROR: Do not use the mutable :latest tag for container base images.
Exit code: 1
```

**Evidence:** uploaded under `docs/screenshots/workstream-A/`

### A4 — clean path

Expected trace:

```text
Python quality       PASS
Semgrep               PASS
pip-audit             PASS
Gitleaks              PASS
Terraform security    PASS
Docker build          PASS
Trivy HIGH/CRITICAL   PASS
```

**Evidence:** uploaded under `docs/screenshots/workstream-A/`

### A5 — high/critical image CVE

The CI Trivy step is configured with `severity: CRITICAL,HIGH`, `ignore-unfixed: true`, and `exit-code: 1`.

Expected behavior: a HIGH/CRITICAL finding causes the job to exit non-zero. Unfixed findings are intentionally ignored to reduce noise; this is a documented policy choice and can be tightened for a production environment.

**Evidence:** uploaded under `docs/screenshots/workstream-A/`

### A false-positive example and handling

A scanner can report a string that resembles a credential or a package finding that is not exploitable in the application's runtime path. The response is **not** to disable the whole scanner. The preferred sequence is:

1. verify the finding;
2. determine whether it is genuinely applicable;
3. update/remove the risky configuration where possible;
4. if suppression is necessary, scope it to the smallest check/resource and document the reason;
5. review suppressions periodically.

---

# B — IaC Security Gates

The Terraform configuration models Azure infrastructure for AKS, ACR, Key Vault, private storage and workload identities. No Azure subscription is required for the challenge.

## B1 — Model/embedding storage is public

Fixture: `iac/evals/public-storage.tf`

Expected controls:

- **Checkov `CKV_AZURE_59`** — storage accounts disallow public access.
- **Checkov `CKV_AZURE_34`** — blob containers use private access.

Expected result: **FAIL**.

Why AI-specific: model artifacts, embeddings and derived customer data may be sensitive. Public access can expose data and can also create a high-volume retrieval path that increases cost or abuse potential.

Expected trace:

```text
Check: CKV_AZURE_59 - Ensure that Storage accounts disallow public access
Result: FAILED

Check: CKV_AZURE_34 - Ensure that 'Public access level' is set to Private for blob containers
Result: FAILED
```

**Evidence:** uploaded under `docs/screenshots/workstream-B/`

## B2 — AI workload identity has excessive permissions

Fixture: `iac/evals/excessive-role.tf`

Expected control: custom Checkov policy **`CKV2_CUSTOM_1`** in `security/checkov_custom/ai_least_privilege.yaml`.

The policy is intentionally an allow-list of roles appropriate to the simulated workload. `Contributor` is not allowed.

Expected result: **FAIL**.

Why AI-specific: if an inference/embedding identity is compromised, a broad control-plane role could let an attacker modify infrastructure, expose data, or create expensive resources. The workload identity should have only the data-plane/resource permissions it actually needs.

Expected trace:

```text
Check: CKV2_CUSTOM_1 - AI workload RBAC uses an approved least-privilege role
Resource: azurerm_role_assignment.ai_identity_contributor
Result: FAILED
Reason: role_definition_name = Contributor is outside the approved role allow-list
```

**Evidence:** uploaded under `docs/screenshots/workstream-B/`

## B3 — API key in Terraform variables

Fixture: `iac/evals/leaked-api-key.tfvars`

Expected controls:

- Checkov secrets framework, including `CKV_SECRET_6` for high-entropy secret material.
- Gitleaks at repository level as the independent secret gate.

Expected result: **FAIL**.

Why AI-specific: LLM/provider credentials can grant data access and can be abused to create unexpected inference/API charges. Terraform variables are not a safe secret store.

Expected trace:

```text
secrets scan results
Check: CKV_SECRET_6 - Base64 High Entropy String
Result: FAILED
```

The exact detector can differ for a deliberately fake test string. The important design property is that the repository has two independent secret controls and no real secret.

**Evidence:** uploaded under `docs/screenshots/workstream-B/`

## B4 — compliant Terraform

The real `iac/` configuration uses:

- storage public network access disabled;
- private blob container access;
- TLS 1.2;
- customer-managed encryption keys;
- private endpoints;
- managed identities rather than embedded credentials;
- narrow resource-scoped role assignments for workload identities;
- private AKS configuration and workload identity support.

Expected result: the security gate passes after any intentionally accepted/suppressed findings are reviewed.

**Evidence:** uploaded under `docs/screenshots/workstream-B/`

---

# C — Cluster Hardening

| ID | Scenario | Expected decision | Control |
|---|---|---|---|
| C1 | Pod runs as root | **DENY** | PSA Restricted + Kyverno `require-non-root` |
| C2 | AI pod has no CPU/memory requests or limits | **DENY** | Kyverno `require-resource-limits` |
| C3 | Pod in `untrusted-workload` attempts to reach embedding service | **DENY** | `embedding-service-ingress` NetworkPolicy |
| C4 | Compliant embedding deployment | **ALLOW** | Non-root, RuntimeDefault seccomp, dropped capabilities, resource limits |

### C1 — root pod

Fixture: `k8s/evals/root-pod.yaml`

Expected Kyverno result:

```text
require-non-root: FAIL
Admission decision: DENY
```

Why: root execution increases the impact of container compromise and is unnecessary for this service.

**Evidence:** uploaded under `docs/screenshots/workstream-C/`

### C2 — no resource limits

Fixture: `k8s/evals/no-resource-limits.yaml`

Expected:

```text
require-resource-limits: FAIL
Admission decision: DENY
```

AI-specific reason: embedding/inference workloads can create large and sudden CPU/RAM consumption. Limits provide a predictable boundary for a shared cluster and reduce noisy-neighbor impact.

**Evidence:** uploaded under `docs/screenshots/workstream-C/`

### C3 — unauthorized namespace

Fixture: `k8s/evals/unauthorized-network-access.yaml`

The network policy allows ingress to `embedding-service` only from namespaces labeled `kubernetes.io/metadata.name: ai-platform`.

Expected runtime network decision:

```text
Source namespace: untrusted-workload
Destination: embedding-service:8000
Decision: DENY
```

A live test requires a NetworkPolicy-capable CNI. The fixture is therefore a design/runtime evaluation rather than proof of a live packet drop.

**Evidence:** uploaded under `docs/screenshots/workstream-C/`

---

# D — Agentic SRE Log Intelligence

The SRE component is a local retrieval-grounded service. It reads synthetic JSON logs, embeds them with `all-MiniLM-L6-v2`, stores vectors and metadata in ChromaDB, retrieves relevant evidence for a natural-language question, and produces a deterministic answer from that evidence. It does not call an external LLM in this challenge.

## D1 — Grounded deployment failure

**Question:** `Why did the last deploy fail?`

**Required evidence:**

```text
2026-09-23T08:57:19Z deployment ERROR Deployment failed: readiness probe failed for pod embedding-service-7d8c9f6d7b-x2k4m
2026-09-23T08:57:20Z kubernetes WARNING Pod embedding-service-7d8c9f6d7b-x2k4m restarted because container exceeded memory limit
2026-09-23T08:58:02Z deployment INFO Deployment rolled back to devsecops-ai-service:7e21b8a
```

**Expected output:**

```text
Based on the retrieved logs:
- ...readiness probe failed...
- ...exceeded memory limit...
- ...Deployment rolled back...

Conclusion: the deployment failed because the readiness probe failed. The affected pod also exceeded its memory limit and was restarted. The deployment was subsequently rolled back.
```

**Pass condition:** the response uses evidence present in the synthetic log file and does not invent a different cause.

**Evidence:** uploaded under `docs/screenshots/workstream-D/`

## D2 — Grounded memory/restart diagnosis

**Question:** `Why was the embedding pod restarted?`

**Expected evidence:**

```text
2026-09-23T08:57:20Z kubernetes WARNING Pod embedding-service-7d8c9f6d7b-x2k4m restarted because container exceeded memory limit
```

**Expected conclusion:**

```text
the embedding-service pod was restarted because the container exceeded its memory limit.
```

**Pass condition:** the memory-limit event is included in retrieved evidence.

**Evidence:** uploaded under `docs/screenshots/workstream-D/`

## D3 — Honest unknown / anti-hallucination

**Question:** `What database caused the payment service outage?`

The synthetic logs contain no payment-service outage and no database root-cause event.

**Expected output:**

```text
I don't know based on the available logs.
```

**Pass condition:** no unsupported database name or root cause is invented.

**Evidence:** uploaded under `docs/screenshots/workstream-D/`

## D4 — Evaluation commands

```bash
python -m pip install -r sre-agent/requirements.txt
pytest -q sre-agent/tests
python sre-agent/app/sre_agent.py "Why did the last deploy fail?"
python sre-agent/app/sre_agent.py "Why was the embedding pod restarted?"
python sre-agent/app/sre_agent.py "What database caused the payment service outage?"
```

The automated tests are in `sre-agent/tests/test_sre_agent.py`. The complete expected transcripts are in `evals/workstream-d/expected-transcripts.md`.

## Why retrieval grounding is important

For an SRE tool, a fluent answer is less useful than a traceable answer. Retrieval grounding constrains the response to evidence that exists in the log corpus. The explicit unknown response prevents the system from inventing an incident cause when the corpus has no supporting event.

`all-MiniLM-L6-v2` is a compact local embedding model suitable for this simulated dataset. ChromaDB provides a local vector store without requiring a managed service.

A production implementation would add authenticated log ingestion, source IDs and timestamps in citations, tenant/namespace authorization, retention controls, prompt/input sanitization, rate limiting, audit logging, real Loki or equivalent ingestion, and model/provider cost controls if an LLM is added for summarization.

# E — Monitoring & Observability

The monitoring artifact consists of Prometheus scrape configuration, Prometheus alert rules, a Grafana dashboard JSON export, and a small local synthetic metrics exporter. The exporter makes the dashboard runnable without a live Kubernetes cluster.

## E1 — Normal week

Fixture: `monitoring/evals/normal-metrics.txt`

```text
ci_pipeline_success_rate_percent 98
pod_restart_count_15m 0
security_policy_denials_per_second 0.02
http_request_rate_per_second 20
http_5xx_rate_percent 0.2
pod_availability_ready 2
```

Expected dashboard interpretation: 98% CI success, zero recent restarts, low policy-denial baseline, low 5xx rate and both simulated pods ready. No incident alert is expected.

**Evidence:** uploaded under `docs/screenshots/workstream-E/`

## E2 — Restart-loop incident

Fixture: `monitoring/evals/incident-restart-loop-metrics.txt`

```text
ci_pipeline_success_rate_percent 98
pod_restart_count_15m 7
security_policy_denials_per_second 0.03
http_request_rate_per_second 20
http_5xx_rate_percent 8.5
pod_availability_ready 1
```

Expected dashboard interpretation: pod restarts and HTTP 5xx increase while ready pods fall from two to one. The relevant alerts are `PodRestartSpike` and `PodRestartLoop`.

**Evidence:** uploaded under `docs/screenshots/workstream-E/`

## E3 — Security policy denial spike

Fixture: `monitoring/evals/incident-policy-denials-metrics.txt`

```text
ci_pipeline_success_rate_percent 98
pod_restart_count_15m 0
security_policy_denials_per_second 3.4
http_request_rate_per_second 21
http_5xx_rate_percent 0.3
pod_availability_ready 2
```

Expected dashboard interpretation: the security-denial panel becomes the dominant signal while application availability remains healthy. The relevant alerts are `SecurityPolicyDenialSpike` and `CriticalSecurityPolicyDenialSpike`, provided the rate remains above their thresholds for the configured duration.

**Evidence:** uploaded under `docs/screenshots/workstream-E/`

## E4 — Alert thresholds and noise control

| Alert | Threshold | Sustained for | Reasoning |
|---|---:|---:|---|
| `PipelineSuccessRateLow` | <90% | 10m | Avoid paging on one failed build; catch sustained delivery degradation |
| `PodRestartSpike` | ≥3 restarts / 15m | 5m | Early investigation signal |
| `PodRestartLoop` | ≥5 restarts / 10m | 5m | Stronger indication of a restart loop |
| `SecurityPolicyDenialSpike` | >0.5 denials/sec | 10m | Detect unusual policy rejection without alerting on isolated tests |
| `CriticalSecurityPolicyDenialSpike` | >2 denials/sec | 5m | Detect sustained high-volume policy failures |

These are starting thresholds for the simulated environment. Production values should be tuned using historical baselines, service-level objectives and the normal deployment pattern.

A noisy alert can happen when a legitimate rollout causes temporary restarts or when developers intentionally test manifests that policy should reject. Sustained `for` periods, separate warning/critical levels and correlated signals reduce unnecessary alerts.

**Evidence:** uploaded under `docs/screenshots/workstream-E/`

## E5 — Run the simulated monitoring evaluations

```bash
# Normal
cp monitoring/evals/normal-metrics.txt monitoring/mock-metrics.txt

docker compose -f monitoring/docker-compose.yml up

# Restart incident: stop the stack, replace the fixture, start again.
cp monitoring/evals/incident-restart-loop-metrics.txt monitoring/mock-metrics.txt

# Security-policy incident
cp monitoring/evals/incident-policy-denials-metrics.txt monitoring/mock-metrics.txt
```

The three fixtures and expected interpretations are also documented in `monitoring/evals/README.md`.
