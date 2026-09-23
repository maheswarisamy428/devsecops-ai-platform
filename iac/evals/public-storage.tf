# INTENTIONALLY INSECURE EVALUATION FIXTURE — DO NOT DEPLOY.
resource "azurerm_storage_account" "ai_model_data_public" {
  name                     = "evalaimodelpublic123"
  resource_group_name      = "eval-rg"
  location                 = "westeurope"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  public_network_access_enabled   = true
  allow_nested_items_to_be_public = true
  min_tls_version                 = "TLS1_2"
}

resource "azurerm_storage_container" "embeddings_public" {
  name                  = "embeddings"
  storage_account_id    = azurerm_storage_account.ai_model_data_public.id
  container_access_type = "blob"
}
