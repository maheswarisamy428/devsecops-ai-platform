## Workstream C — Cluster Hardening

| Eval | Scenario | Expected result | Control |
|---|---|---|---|
| C1 | Pod requests root | DENY | PSA Restricted + Kyverno |
| C2 | AI pod has no CPU/memory limits | DENY | Kyverno |
| C3 | Pod in untrusted namespace accesses embedding service | DENY | NetworkPolicy |

### C1 — Root container

`k8s/evals/root-pod.yaml`

Expected admission decision: **DENY**

The restricted Pod Security profile requires workloads to run without root privileges.

### C2 — Missing resource limits

`k8s/evals/no-resource-limits.yaml`

Expected admission decision: **DENY**

AI workloads can consume significantly more CPU, memory and potentially GPU resources during inference, embedding generation or unexpected workload spikes. Resource requests and limits reduce noisy-neighbor impact and prevent a single workload from consuming unbounded cluster capacity.

### C3 — Unauthorized network access

`k8s/evals/unauthorized-network-access.yaml`

Expected network decision: **DENY**

The embedding service accepts traffic only from workloads in the approved `ai-platform` namespace. Namespace isolation reduces the blast radius if another AI or application workload is compromised.