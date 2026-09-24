# DevSecOps AI Platform — End-to-End Challenge

## 1. Purpose and scope

This repository is a **simulated DevSecOps design and evaluation project** for a small AI-assisted FastAPI microservice.

The challenge explicitly does **not** require a fully deployed production system. The repository therefore contains real code, configuration, policies, CI definitions and evaluation fixtures, while cloud infrastructure, cluster enforcement and some observability integrations are intentionally represented through local execution or documented simulations.

The goal is to demonstrate that the security and observability controls are coherent, testable and explainable — not to claim that a production Azure/Kubernetes environment was operated during this challenge.

### What this repository does claim

- The configuration and source artifacts are real repository artifacts.
- The local application, SRE agent, tests and selected security tools can be run locally when their dependencies are installed.
- Terraform can be formatted/validated without connecting to Azure.
- Security evaluation fixtures are intentionally designed to produce expected failures.
- Prometheus/Grafana configuration is provided, with a local mock metrics path for simulated monitoring scenarios.
- The SRE agent uses synthetic logs generated for this challenge and performs grounded local retrieval.

### What this repository does **not** claim

- No production Azure subscription or production Kubernetes cluster was deployed as part of this submission.
- No claim is made that a real cloud resource, Kubernetes admission event or network packet was blocked unless the corresponding local command was actually executed and evidence was captured.
- The synthetic SRE logs are not production telemetry.
- The Grafana dashboard is not presented as evidence of a live production monitoring system.
- The evaluation outputs described in `EVALS.md` are expected outcomes unless an **Observed** result has been added from an actual local/CI run.

For the exact simulation boundaries and trade-offs, see [`DECISIONS.md`](DECISIONS.md).

## 2. Workstreams

| Workstream | Real artifacts | Evaluation scope |
|---|---|---|
| **A — Secure CI/CD** | GitHub Actions, Semgrep, pip-audit, Gitleaks, Trivy configuration and fixtures | Local/tool or CI evaluation; no production deployment required |
| **B — IaC Security** | Terraform, Checkov/tfsec configuration, custom Checkov policy and negative fixtures | Terraform/static IaC evaluation; no Azure resources required |
| **C — Cluster Hardening** | Kubernetes manifests, PSA-related settings, Kyverno policies, RBAC and NetworkPolicy | Manifest/policy evaluation; live admission/network enforcement is simulated unless locally executed |
| **D — Agentic SRE** | Python retrieval service, sentence-transformers, ChromaDB and synthetic logs | Local runnable component using synthetic data |
| **E — Monitoring & Observability** | Prometheus config, Grafana dashboard JSON, alert rules and mock exporter | Local/mock monitoring evaluation; no production metrics source required |

## 3. End-to-end architecture

```text
Developer PR
    |
    +--> Quality checks
    +--> Semgrep SAST
    +--> pip-audit SCA
    +--> Gitleaks secret scan
    |             |
    +-------------+----> security gates
                  |
                  v
          Terraform / Checkov / tfsec
                  |
                  v
             Docker build
                  |
                  v
        Trivy HIGH/CRITICAL gate
                  |
                  v
       Kubernetes policy evaluation
                  |
                  v
        AI-assisted FastAPI service
             /             \
        logs/metrics       policies
           |                   |
     Prometheus/Grafana   Kyverno/NetworkPolicy
           |                   |
           +-------> SRE log intelligence
                         |
                  synthetic logs in
                    this challenge
```

The architecture is deliberately split into **source/build controls**, **infrastructure controls**, **runtime controls**, and **observability/SRE controls**.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the detailed walkthrough, trust boundaries and failure-path analysis.

## 4. Repository structure

```text
.github/workflows/       GitHub Actions security pipeline
security/                Semgrep, Trivy and custom Checkov policies
iac/                     Terraform and IaC evaluation fixtures
k8s/                     Kubernetes manifests and negative policy fixtures
evals/                   Simulated evaluation fixtures and validation
sre-agent/               Local grounded SRE log-intelligence component
monitoring/              Prometheus, Grafana, alert rules and mock metrics
docs/screenshots/        Evidence directories for A–E screenshots
EVALS.md                 Full simulated evaluation suite
ARCHITECTURE.md          End-to-end architecture and control mapping
DECISIONS.md             Design trade-offs and simulation boundaries
AI_USAGE.md              AI coding-assistance disclosure
tests/                   contains the automated test cases.
README.md                explicitly listed with its purpose: setup, requirements, testing, and project documentation
```

## 5. Runnable vs. simulated/conceptual components

### 5.1 Runnable locally

The following are intended to be executable locally, subject to the required tools/dependencies being installed:

- FastAPI application and unit tests.
- SRE agent against the supplied synthetic JSON logs.
- SRE agent tests.
- Terraform `fmt` and `validate` without a cloud backend.
- Checkov, tfsec, Semgrep, Gitleaks, pip-audit and Trivy when installed locally.
- Prometheus/Grafana mock monitoring stack through Docker Compose, where the local Docker environment supports it.
- Repository-level evaluation/consistency checks.

### 5.2 Simulated or conceptual

The following are intentionally **not represented as live production evidence**:

- Azure infrastructure deployment.
- AKS cluster deployment and real Pod Security Admission enforcement.
- Real Kubernetes network packet enforcement through a production CNI.
- Production log ingestion through Loki or another centralized log platform.
- Production application metrics generated by a real workload.
- Real alert firing against a production Alertmanager instance.
- Real LLM/provider calls for the SRE agent.
- Production-scale authentication, authorization, retention and cost controls.

Where a component is simulated, `EVALS.md` describes the stimulus, expected control, expected result and evidence to capture.

## 6. Local setup

### Prerequisites

Install only the open-source tools needed for the workstream you want to execute. A complete local run may include:

- Python 3.x
- Docker / Docker Compose
- Terraform
- Checkov
- tfsec
- Semgrep
- Gitleaks
- Trivy
- Git

A live Azure account is **not required** for the challenge evaluation.

### Application tests

```bash
python -m pip install -r requirements.txt -r dev_requirements.txt -r test_requirements.txt
pytest -q tests
```

This validates the application/test layer only. A successful local test run is not evidence of a deployed production service.

### Terraform validation

```bash
terraform -chdir=iac fmt -check -recursive
terraform -chdir=iac init -backend=false
terraform -chdir=iac validate
```

These commands validate Terraform configuration locally. They do not provision Azure resources.

### IaC security evaluation

```bash
checkov -d iac --framework terraform --config-file iac/checkov.yaml
checkov -d iac --framework terraform --external-checks-dir security/checkov_custom --check CKV2_CUSTOM_1
checkov -d iac --framework secrets
```

The files under `iac/evals/` deliberately contain insecure examples. They are evaluation fixtures and must **not** be applied.

### SAST, dependency and secret scanning

Examples:

```bash
semgrep scan --config security/semgrep.yml .
pip-audit -r requirements.txt

gitleaks dir . --no-banner
```

The CI workflow in `.github/workflows/security-pipeline.yml` combines the relevant gates. The expected failure scenarios are documented in `EVALS.md`.

### Container scanning

Build the image locally if Docker is available, then scan the resulting image with Trivy. The CI policy is configured to fail on HIGH/CRITICAL findings according to the documented challenge policy.

The challenge does not claim that a production image registry was used.

### SRE agent

```bash
python -m pip install -r sre-agent/requirements.txt -r test_requirements.txt
pytest -q sre-agent/tests

python sre-agent/app/sre_agent.py "Why did the last deploy fail?"
python sre-agent/app/sre_agent.py "Why was the embedding pod restarted?"
python sre-agent/app/sre_agent.py "What database caused the payment service outage?"
```

The agent operates on `sre-agent/logs/synthetic_logs.json`. The third question is intentionally unsupported by the dataset and should result in an explicit **I don't know based on the available logs** response rather than an invented explanation.

This is a local retrieval/evaluation component; it is not connected to production logs or an external LLM provider in this challenge.

### Monitoring simulation

If Docker Compose is available:

```bash
docker compose -f monitoring/docker-compose.yml up --build
```

The mock exporter reads representative values from `monitoring/mock-metrics.txt`. The files under `monitoring/evals/` provide normal and incident scenarios.

Changing the mock values demonstrates how the dashboard and alert rules are intended to respond. This is **simulated monitoring data**, not telemetry from a live production workload.

## 7. Evaluation and evidence

`EVALS.md` is the authoritative evaluation map for the challenge. Each scenario identifies:

1. the stimulus;
2. the security/observability control;
3. the expected outcome;
4. the expected trace or answer where applicable; and
5. the evidence that should be captured after an actual local/CI run.

Screenshots are intentionally organized generically by workstream:

```text
docs/screenshots/workstream-A/
docs/screenshots/workstream-B/
docs/screenshots/workstream-C/
docs/screenshots/workstream-D/
docs/screenshots/workstream-E/
```

The documentation does not depend on specific screenshot filenames. Add the final terminal/UI captures to the appropriate workstream directory after running the relevant evaluation.

### Expected vs. observed evidence

The repository distinguishes between:

- **Expected:** what the design is intended to do.
- **Observed:** what was actually produced by a local/CI execution.

If an evaluation has not been executed, its expected output must not be presented as an observed production result.

## 8. Security boundaries and test fixtures

Several files intentionally contain insecure configurations so that the controls can be evaluated. Examples include:

- vulnerable dependency fixtures;
- hardcoded fake credentials;
- mutable container tags;
- public storage configuration;
- excessive IAM/RBAC assignments;
- root Kubernetes pods;
- missing resource limits;
- unauthorized network access scenarios.

These fixtures are **negative test inputs only**. They must never be deployed, applied or promoted.

No real credentials, cloud secrets, customer data or paid licenses should be committed.

## 9. Security design principles

The project applies several layers rather than relying on one scanner or one policy:

- **SAST/SCA/secret scanning** catches source and dependency problems early.
- **IaC security** prevents insecure cloud configuration from reaching deployment.
- **Container scanning** checks the actual build artifact.
- **Kubernetes policies** provide runtime admission and workload hardening controls.
- **NetworkPolicy** limits service-to-service reachability.
- **Resource limits** provide predictable boundaries for potentially resource-intensive AI workloads.
- **Observability** provides operational and security signals.
- **Grounded SRE retrieval** prevents the log assistant from inventing incident causes when evidence is absent.

The controls are complementary. `ARCHITECTURE.md` and `DECISIONS.md` explain what coverage is lost if a control is skipped.

## 10. AI usage disclosure

AI coding assistance was used during development of this challenge. The actual assistance, boundaries and review responsibility are documented in [`AI_USAGE.md`](AI_USAGE.md).

The candidate remains responsible for understanding and being able to explain the submitted code, configuration and design decisions.

## 11. Submission checklist

Before submitting the repository:

- [ ] Public GitHub repository created.
- [ ] Incremental commit history retained.
- [ ] All five workstreams represented.
- [ ] `EVALS.md` reviewed and updated with actual observed evidence where available.
- [ ] `ARCHITECTURE.md` reviewed and understood end-to-end.
- [ ] `DECISIONS.md` clearly distinguishes runnable work from simulated/conceptual work.
- [ ] `AI_USAGE.md` reflects the actual AI assistance used.
- [ ] Screenshots added under the appropriate `docs/screenshots/workstream-*` directory.
- [ ] No real credentials or paid-tool dependencies committed.
- [ ] Negative evaluation fixtures are not deployed or applied.

## 12. Final scope statement

**This repository should be evaluated as a coherent, security-focused DevSecOps reference implementation with reproducible simulations — not as a claim of a live production Azure/Kubernetes platform.**

The strongest evidence is the combination of real configuration/code, deliberately negative fixtures, documented expected behavior, and locally captured observed results where the candidate has actually executed the tests.
