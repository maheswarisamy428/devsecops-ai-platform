output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "aks_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "acr_name" {
  value = azurerm_container_registry.main.name
}

output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "storage_account_name" {
  value = azurerm_storage_account.ai_data.name
}

output "key_vault_name" {
  value = azurerm_key_vault.main.name
}

output "ai_workload_identity_client_id" {
  value = azurerm_user_assigned_identity.ai_workload.client_id
}
