# Terraform Infrastructure

This directory contains the Azure infrastructure definition for the
DevSecOps AI microservice challenge.

## Infrastructure

The Terraform configuration provisions:

- Azure Resource Group
- Azure Virtual Network
- AKS
- Azure Container Registry
- Azure Storage
- Azure Key Vault
- Managed Identity
- Log Analytics
- Azure RBAC
- AKS Workload Identity

## Terraform State

Terraform state is stored remotely in Azure Blob Storage using the
`azurerm` backend.

The state storage is bootstrapped separately from the main Terraform
configuration.

Authentication should use Microsoft Entra ID / OIDC rather than
storage account keys.

## Validation

Run:

```bash
terraform fmt -check -recursive
terraform validate
tflint
checkov -d .
tfsec .