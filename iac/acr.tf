resource "azurerm_container_registry" "main" {
  name = replace(
    "${var.project_name}${var.environment}acr",
    "-",
    ""
  )

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku = "Standard"

  admin_enabled = false

  public_network_access_enabled = true

  tags = var.tags
}