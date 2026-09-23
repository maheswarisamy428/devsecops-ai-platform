data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name = "${var.project_name}-${var.environment}-kv"

  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tenant_id = data.azurerm_client_config.current.tenant_id

  sku_name = "premium"

  rbac_authorization_enabled = true

  purge_protection_enabled   = true
  soft_delete_retention_days = 90

  # CKV_AZURE_109
  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }

  public_network_access_enabled = false

  tags = var.tags
}


resource "azurerm_private_endpoint" "key_vault" {
  name                = "${var.project_name}-${var.environment}-kv-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  subnet_id = azurerm_subnet.private_endpoints.id

  private_service_connection {
    name                           = "${var.project_name}-${var.environment}-kv-psc"
    private_connection_resource_id = azurerm_key_vault.main.id
    is_manual_connection           = false
    subresource_names              = ["vault"]
  }

  tags = var.tags
}


resource "azurerm_key_vault_key" "aks" {
  name         = "aks-encryption-key"
  key_vault_id = azurerm_key_vault.main.id

  key_type        = "RSA-HSM"
  key_size        = 4096
  expiration_date = "2030-12-31T23:59:59Z"

  key_opts = [
    "decrypt",
    "encrypt",
    "unwrapKey",
    "wrapKey"
  ]

  depends_on = [
    azurerm_key_vault.main
  ]
}

resource "azurerm_key_vault_key" "storage" {
  name         = "storage-encryption-key"
  key_vault_id = azurerm_key_vault.main.id

  key_type        = "RSA-HSM"
  key_size        = 4096
  expiration_date = "2030-12-31T23:59:59Z"

  key_opts = [
    "decrypt",
    "encrypt",
    "unwrapKey",
    "wrapKey"
  ]
}
