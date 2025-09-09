output "service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.production.uri
}

output "artifact_registry_repository_url" {
  description = "Artifact Registry repository URL"
  value       = google_artifact_registry_repository.nomadly.name
}

output "github_actions_service_account" {
  description = "GitHub Actions service account email"
  value       = data.google_service_account.github_actions.email
}

output "workload_identity_provider" {
  description = "Workload Identity Provider for GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}