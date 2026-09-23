#checkov:skip=CKV_AZURE_164: AzureRM v5 does not expose ACR trusted image policy controls.
resource "azurerm_container_registry" "main" {
  name = replace(
    "${var.project_name}${var.environment}acr",
    "-",
    ""
  )

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku = "Premium"

  admin_enabled = false

  public_network_access_enabled = false
  data_endpoint_enabled         = true

  retention_policy_in_days  = 30
  quarantine_policy_enabled = true
  zone_redundancy_enabled   = true

  georeplications {
    location                = var.secondary_location
    zone_redundancy_enabled = true
  }

  tags = var.tags
}

variable "secondary_location" {
  type        = string
  description = "Secondary Azure region for ACR geo-replication"
  default     = "North Europe"
}