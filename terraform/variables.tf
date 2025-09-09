variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "paradox-intern"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "asia-northeast3"
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "nomadly-api"
}

variable "artifact_registry_repository" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "nomadly"
}

variable "github_owner" {
  description = "GitHub repository owner/organization"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}


variable "database_url" {
  description = "Database connection URL (will be stored in Secret Manager)"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT secret key (will be stored in Secret Manager)"
  type        = string
  sensitive   = true
}

