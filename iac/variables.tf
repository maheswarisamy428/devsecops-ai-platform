variable "project_name" {
  type        = string
  description = "Project name."

  default = "devsecops-ai"
}

variable "environment" {
  type        = string
  description = "Environment name."

  default = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be dev, test, or prod."
  }
}

variable "location" {
  type        = string
  description = "Azure region."

  default = "westeurope"
}

variable "tags" {
  type        = map(string)
  description = "Common resource tags."

  default = {
    project    = "devsecops-challenge"
    managed_by = "terraform"
    purpose    = "simulated-ai-microservice"
  }
}

variable "aks_api_server_authorized_ip_ranges" {
  type        = list(string)
  description = "CIDR ranges allowed to access the AKS API server"
}