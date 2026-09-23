resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-${var.environment}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  dns_prefix = "${var.project_name}-${var.environment}"

  sku_tier = "Free"

  default_node_pool {
    name       = "system"
    vm_size    = "Standard_D2s_v5"
    node_count = 1

    vnet_subnet_id = azurerm_subnet.aks.id

    only_critical_addons_enabled = true

    upgrade_settings {
      max_surge = "10%"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    network_policy      = "cilium"
    network_data_plane  = "cilium"
    load_balancer_sku   = "standard"
  }

  role_based_access_control_enabled = true

  azure_policy_enabled = true

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  tags = var.tags
}

resource "azurerm_kubernetes_cluster_node_pool" "workload" {
  name                  = "workload"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id

  mode = "User"

  vm_size    = "Standard_D2s_v5"
  node_count = 1

  vnet_subnet_id = azurerm_subnet.aks.id

  node_labels = {
    workload = "application"
  }

  tags = var.tags
}
