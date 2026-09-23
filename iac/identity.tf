resource "azurerm_user_assigned_identity" "ai_workload" {
  name = "${var.project_name}-${var.environment}-ai-mi"

  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_user_assigned_identity" "storage" {
  name                = "${var.project_name}-${var.environment}-storage-uai"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = var.tags
}