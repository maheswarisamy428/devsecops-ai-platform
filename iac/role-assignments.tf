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