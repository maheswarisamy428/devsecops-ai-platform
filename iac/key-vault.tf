data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name = "${var.project_name}-${var.environment}-kv"

  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tenant_id = data.azurerm_client_config.current.tenant_id

  sku_name = "standard"

  rbac_authorization_enabled = true

  purge_protection_enabled   = true
  soft_delete_retention_days = 90

  public_network_access_enabled = false

  tags = var.tags
}