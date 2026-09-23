resource "azurerm_storage_account" "ai_data" {
  name = replace(
    "${var.project_name}${var.environment}aistorage",
    "-",
    ""
  )

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  account_tier             = "Standard"
  account_replication_type = "LRS"

  min_tls_version = "TLS1_2"

  public_network_access_enabled = false

  shared_access_key_enabled = false

  allow_nested_items_to_be_public = false

  infrastructure_encryption_enabled = true

  blob_properties {
    versioning_enabled = true
  }

  tags = var.tags
}

resource "azurerm_storage_container" "embeddings" {
  name = "embeddings"

  storage_account_id = azurerm_storage_account.ai_data.id

  container_access_type = "private"
}