resource "azurerm_role_assignment" "ai_storage_reader" {
  scope = azurerm_storage_account.ai_data.id

  role_definition_name = "Storage Blob Data Reader"

  principal_id = azurerm_user_assigned_identity.ai_workload.principal_id
}

resource "azurerm_role_assignment" "ai_keyvault_reader" {
  scope = azurerm_key_vault.main.id

  role_definition_name = "Key Vault Secrets User"

  principal_id = azurerm_user_assigned_identity.ai_workload.principal_id
}

resource "azurerm_role_assignment" "aks_acr_pull" {
  scope = azurerm_container_registry.main.id

  role_definition_name = "AcrPull"

  principal_id = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

resource "azurerm_role_assignment" "aks_disk_encryption" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Crypto Service Encryption User"
  principal_id         = azurerm_disk_encryption_set.aks.identity[0].principal_id
}

resource "azurerm_role_assignment" "storage_key" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Crypto Service Encryption User"
  principal_id         = azurerm_user_assigned_identity.storage.principal_id
}
