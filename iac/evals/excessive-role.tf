# INTENTIONALLY INSECURE EVALUATION FIXTURE — DO NOT DEPLOY.
resource "azurerm_role_assignment" "ai_identity_contributor" {
  scope                = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/eval-rg"
  role_definition_name = "Contributor"
  principal_id         = "00000000-0000-0000-0000-000000000000"
}
