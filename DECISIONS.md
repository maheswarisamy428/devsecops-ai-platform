# Design Decisions and Trade-offs

## Decision 1 — Simulated cloud instead of a live Azure environment

**Choice:** Keep Terraform real and validate it with `fmt`, `init -backend=false`, `validate`, Checkov and tfsec, but do not provision Azure resources.

**Why:** The challenge explicitly prioritizes coherent security design and evaluation over cloud spend. This also makes the repository safe to run without credentials.

**Trade-off:** Terraform validation cannot prove that the exact Azure subscription policies, quotas, permissions or provider-side behavior will succeed.

**Next:** Run the same plan through a disposable Azure subscription with OIDC and policy assignments.

## Decision 2 — Checkov plus a small custom IAM policy

**Choice:** Use built-in Checkov checks for cloud hygiene and a custom Checkov policy for the simulated AI workload RBAC allow-list.

**Why:** A generic scanner can detect known configuration problems, but semantic least privilege is application-specific. The custom policy makes the intended AI identity boundary executable.

**Trade-off:** The allow-list must be reviewed whenever workload permissions change. It is not a substitute for a full Azure RBAC review.

## Decision 3 — Gitleaks for repository secrets

**Choice:** Use Gitleaks as the primary repository-level secret detector and Checkov secret scanning as an IaC-focused second signal.

**Why:** Independent scanners reduce reliance on one detector and cover different file/configuration contexts.

**Trade-off:** Duplicate findings require triage. False positives must be suppressed narrowly and documented.

## Decision 4 — Semgrep for the `:latest` Dockerfile policy

**Choice:** Encode the mutable base-image rule as a small Semgrep Dockerfile rule.

**Why:** It is transparent, version-controlled and easy to demonstrate in an evaluation fixture.

**Trade-off:** The rule does not prove that every third-party tag is immutable. Production should prefer digests for stronger reproducibility.

## Decision 5 — Kyverno + Pod Security Admission

**Choice:** Use PSA Restricted as the platform baseline and Kyverno for workload-specific rules.

**Why:** PSA provides a Kubernetes-native baseline while Kyverno expresses organization-specific controls such as resource limits.

**Trade-off:** Policies must be tested against the exact Kubernetes/Kyverno versions in use. A policy engine cannot compensate for an unsupported CNI or weak identity configuration.

## Decision 6 — NetworkPolicy instead of application-only authorization

**Choice:** Restrict east-west traffic with NetworkPolicy and keep application authorization separate.

**Why:** NetworkPolicy reduces reachable services after compromise; application authentication/authorization controls what an allowed caller can actually do.

**Trade-off:** A NetworkPolicy requires a compatible CNI and does not provide user-level authorization.

## Decision 7 — Local embeddings + Chroma, no external LLM

**Choice:** Use `all-MiniLM-L6-v2` and Chroma locally; derive answers deterministically from retrieved evidence.

**Why:** It keeps the challenge reproducible, open-source and free of external data/API dependencies. It also makes the anti-hallucination behavior directly testable.

**Trade-off:** The answer quality is less flexible than a strong generative model. A production version could add a local or approved LLM behind strict grounding and access controls.

## Decision 8 — Mock metrics instead of claiming live observability

**Choice:** Provide Prometheus rules, Grafana JSON and a mock exporter.

**Why:** The challenge permits simulated metrics and does not require live infrastructure.

**Trade-off:** Dashboard queries are representative rather than validated against a production Prometheus schema.

## Decision 9 — HIGH/CRITICAL blocking policy

**Choice:** Trivy blocks HIGH/CRITICAL findings and ignores unfixed findings in this seven-day simulation.

**Why:** It creates a clear acceptance gate without turning every upstream unfixed issue into an automatic blocker.

**Trade-off:** Ignoring unfixed vulnerabilities leaves residual risk. A production policy should define an exception/expiry process and may choose to block based on exploitability and runtime exposure.

## Decision 10 — Evidence is explicitly labeled

**Choice:** Documentation distinguishes expected behavior from observed tool output and leaves screenshot placeholders.

**Why:** The acceptance criteria require honest claims about what is simulated. No live production posture is claimed.
