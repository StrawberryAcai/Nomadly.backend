terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------------------------------------------------
# Enable required APIs
# -----------------------------------------------------------

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# -----------------------------------------------------------
# Artifact Registry repository for container images
# -----------------------------------------------------------

resource "google_artifact_registry_repository" "nomadly" {
  repository_id = var.artifact_registry_repository
  format        = "DOCKER"
  location      = var.region
  description   = "Docker repository for Nomadly API"

  depends_on = [google_project_service.artifactregistry]
}

# -----------------------------------------------------------
# Service account for GitHub Actions (이미 수동 생성됨 → data로 참조)
# -----------------------------------------------------------

data "google_service_account" "github_actions" {
  account_id = "github-actions"
  project    = var.project_id
}

# IAM roles for GitHub Actions service account
resource "google_project_iam_member" "github_actions_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${data.google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_serviceaccount_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${data.google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${data.google_service_account.github_actions.email}"
}

resource "google_project_iam_member" "github_actions_artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${data.google_service_account.github_actions.email}"
}

# -----------------------------------------------------------
# Production Cloud Run service
# -----------------------------------------------------------

resource "google_cloud_run_v2_service" "production" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}/nomadly-api:latest"

      ports {
        container_port = 8000
      }

      env {
        name  = "JWT_ALGORITHM"
        value = "HS256"
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "JWT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jwt_secret.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    timeout = "300s"
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [
    google_project_service.run,
    google_artifact_registry_repository.nomadly,
    google_project_service.secretmanager
  ]
}

# IAM policy for unauthenticated access
resource "google_cloud_run_service_iam_member" "production_invoker" {
  location = google_cloud_run_v2_service.production.location
  service  = google_cloud_run_v2_service.production.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# -----------------------------------------------------------
# Secret Manager for sensitive environment variables
# -----------------------------------------------------------

resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret"

  replication {
    auto {}
  }

  depends_on = [google_project_service.secretmanager]
}

# -----------------------------------------------------------
# Workload Identity Pool & Provider for GitHub Actions
# -----------------------------------------------------------

resource "google_iam_workload_identity_pool" "github_pool" {
  project                   = var.project_id
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Identity pool for GitHub Actions"
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Provider"
  description                        = "OIDC identity pool provider for GitHub Actions"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Allow GitHub Actions to impersonate the service account
resource "google_service_account_iam_member" "github_actions_workload_identity" {
  service_account_id = data.google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_owner}/${var.github_repo}"
}

# -----------------------------------------------------------
# Project metadata
# -----------------------------------------------------------

data "google_project" "current" {
  project_id = var.project_id
}