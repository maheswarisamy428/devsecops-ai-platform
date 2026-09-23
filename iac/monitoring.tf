resource "azurerm_log_analytics_workspace" "main" {
  name = "${var.project_name}-${var.environment}-logs"

  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku               = "PerGB2018"
  retention_in_days = 30

  tags = var.tags
}

resource "azurerm_monitor_diagnostic_setting" "storage_blob" {
  name               = "${var.project_name}-${var.environment}-storage-blob-logs"
  target_resource_id = azurerm_storage_account.ai_data.id

  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "StorageRead"
  }

  enabled_log {
    category = "StorageWrite"
  }

  enabled_log {
    category = "StorageDelete"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

resource "azurerm_monitor_diagnostic_setting" "storage_queue" {
  name               = "${var.project_name}-${var.environment}-storage-queue-logs"
  target_resource_id = azurerm_storage_account.ai_data.id

  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "StorageRead"
  }

  enabled_log {
    category = "StorageWrite"
  }

  enabled_log {
    category = "StorageDelete"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

resource "azurerm_storage_account_queue_properties" "ai_data" {
  storage_account_id = azurerm_storage_account.ai_data.id

  logging {
    version               = "1.0"
    delete                = true
    read                  = true
    write                 = true
    retention_policy_days = 7
  }
}
