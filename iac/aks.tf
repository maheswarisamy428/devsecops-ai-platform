resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-${var.environment}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  dns_prefix = "${var.project_name}-${var.environment}"

  # CKV_AZURE_170
  sku_tier                  = "Standard"
  automatic_upgrade_channel = "stable"

  node_provisioning_profile {
    mode = "Auto"
  }

  # CKV_AZURE_115
  private_cluster_enabled = true

  # CKV_AZURE_117
  disk_encryption_set_id = azurerm_disk_encryption_set.aks.id

  # CKV_AZURE_141
  local_account_disabled = true

  default_node_pool {
    name       = "system"
    vm_size    = "Standard_D2s_v5"
    node_count = 1

    vnet_subnet_id = azurerm_subnet.aks.id

    only_critical_addons_enabled = true

    # CKV_AZURE_168
    max_pods = 50

    # CKV_AZURE_226
    os_disk_type = "Ephemeral"

    # CKV_AZURE_227
    host_encryption_enabled = true

    upgrade_settings {
      max_surge = "10%"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  # CKV_AZURE_172
  key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2m"
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

  # CKV_AZURE_168
  max_pods = 50

  # CKV_AZURE_227
  host_encryption_enabled = true

  # CKV_AZURE_226
  os_disk_type = "Ephemeral"

  node_labels = {
    workload = "application"
  }

  tags = var.tags
}

resource "azurerm_disk_encryption_set" "aks" {
  name                = "${var.project_name}-${var.environment}-des"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  key_vault_key_id = azurerm_key_vault_key.aks.id

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}