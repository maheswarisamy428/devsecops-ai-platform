# Workstream B evaluation fixtures

These files are deliberately insecure and exist only to demonstrate that the IaC security gate detects AI-specific failure modes. They must never be applied with Terraform.

| Fixture | Scenario | Expected control |
|---|---|---|
| `public-storage.tf` | Model/embedding storage is publicly reachable | Checkov `CKV_AZURE_59` for storage-account public access; `CKV_AZURE_34` for public blob container access |
| `excessive-role.tf` | AI workload identity receives `Contributor` | Custom Checkov `CKV2_CUSTOM_1` allow-list rejects non-approved RBAC roles |
| `leaked-api-key.tfvars` | LLM/API credential is committed in IaC variables | Checkov secret scanning, especially `CKV_SECRET_6`; Gitleaks is the second independent secret gate |

Example local commands:

```bash
checkov -d iac/evals --framework terraform --check CKV_AZURE_59,CKV_AZURE_34
checkov -d iac/evals --framework terraform --external-checks-dir security/checkov_custom --check CKV2_CUSTOM_1
checkov -d iac/evals --framework secrets --check CKV_SECRET_6
```

The exact secret detector can vary with the scanner version and the shape of a test string. Gitleaks remains the repository-level secret gate in Workstream A.
