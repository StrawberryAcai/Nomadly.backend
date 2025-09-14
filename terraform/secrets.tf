# Secret versions for storing actual secret values
# These will be populated manually or via terraform apply with -var flags

resource "google_secret_manager_secret_version" "database_url" {
  count       = var.database_url != "" && var.database_url != null ? 1 : 0
  secret      = google_secret_manager_secret.database_url.id
  secret_data = var.database_url

  lifecycle {
    ignore_changes = [secret_data]
  }
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  count       = var.jwt_secret != "" && var.jwt_secret != null ? 1 : 0
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = var.jwt_secret

  lifecycle {
    ignore_changes = [secret_data]
  }
}


# IAM binding for Cloud Run to access secrets
resource "google_secret_manager_secret_iam_member" "database_url_accessor" {
  secret_id = google_secret_manager_secret.database_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "jwt_secret_accessor" {
  secret_id = google_secret_manager_secret.jwt_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
}

