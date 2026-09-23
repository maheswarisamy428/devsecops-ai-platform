# Workstream A evaluation fixtures

| Fixture | Scenario | Expected result |
|---|---|---|
| `vulnerable-requirements.txt` | Known-vulnerable dependency is introduced | `pip-audit` reports a vulnerability and exits non-zero |
| `hardcoded-secret.txt` | API credential is committed | Gitleaks reports a secret and exits non-zero |
| `Dockerfile.latest` | Mutable `:latest` base image is introduced | Semgrep `docker-no-latest-tag` reports an ERROR and the gate fails |
| clean repository | No findings | All gates pass and the image proceeds to Trivy |

The vulnerable dependency is an evaluation fixture only. CVE/advisory identifiers should be captured from the `pip-audit` version used for the evaluation run rather than hard-coded into the repository documentation.
