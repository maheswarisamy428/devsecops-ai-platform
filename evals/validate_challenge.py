"""Static validation of the challenge deliverables.

This does not claim to replace the real security scanners. It checks that the
expected artifacts and deliberately negative fixtures are present.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "ARCHITECTURE.md",
    "DECISIONS.md",
    "AI_USAGE.md",
    "EVALS.md",
    ".github/workflows/security-pipeline.yml",
    "security/semgrep.yml",
    "security/checkov_custom/ai_least_privilege.yaml",
    "iac/evals/public-storage.tf",
    "iac/evals/excessive-role.tf",
    "iac/evals/leaked-api-key.tfvars",
    "k8s/kyverno-policies.yaml",
    "k8s/network-policy.yaml",
    "sre-agent/app/sre_agent.py",
    "monitoring/prometheus.yml",
    "monitoring/alerts.yml",
    "monitoring/grafana/dashboard.json",
]

for relative in REQUIRED:
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {relative}")

workflow = (ROOT / ".github/workflows/security-pipeline.yml").read_text()
required_tokens = [
    "pip-audit",
    "gitleaks/gitleaks-action",
    "semgrep/semgrep-action",
    "aquasecurity/trivy-action",
    "severity: CRITICAL,HIGH",
    'exit-code: "1"',
    "soft_fail: false",
]

for token in required_tokens:
    if token not in workflow:
        raise SystemExit(f"Pipeline is missing required security gate: {token}")

print("Challenge artifact validation: PASS")
print(f"Checked {len(REQUIRED)} required artifacts")
print("Verified CI contains SAST, SCA, secret, IaC and HIGH/CRITICAL image gates")
