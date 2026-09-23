resource "azurerm_storage_account" "ai_data" {
  name = replace(
    "${var.project_name}${var.environment}aistorage",
    "-",
    ""
  )

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  account_tier             = "Standard"
  account_replication_type = "GRS"

  min_tls_version = "TLS1_2"

  public_network_access_enabled = false

  shared_access_key_enabled = false

  allow_nested_items_to_be_public = false

  infrastructure_encryption_enabled = true

  identity {
    type = "UserAssigned"

    identity_ids = [
      azurerm_user_assigned_identity.storage.id
    ]
  }

  customer_managed_key {
    key_vault_key_id          = azurerm_key_vault_key.storage.id
    user_assigned_identity_id = azurerm_user_assigned_identity.storage.id
  }

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 30
    }

    container_delete_retention_policy {
      days = 30
    }
  }

  tags = var.tags
}

resource "azurerm_storage_container" "embeddings" {
  name = "embeddings"

  storage_account_id = azurerm_storage_account.ai_data.id

  container_access_type = "private"
}

resource "azurerm_private_endpoint" "storage" {
  name                = "${var.project_name}-${var.environment}-storage-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  subnet_id = azurerm_subnet.private_endpoints.id

  private_service_connection {
    name                           = "${var.project_name}-${var.environment}-storage-psc"
    private_connection_resource_id = azurerm_storage_account.ai_data.id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }

  tags = var.tags
}

resource "azurerm_storage_account_network_rules" "ai_data" {
  storage_account_id = azurerm_storage_account.ai_data.id

  default_action = "Deny"
  bypass         = ["AzureServices"]
}
