#!/bin/bash
set -e

echo "Checking and importing existing resources..."

# Function to check if resource exists in state
resource_exists() {
    terraform state show "$1" >/dev/null 2>&1
}

# Function to check if GCP resource exists
gcp_resource_exists() {
    local resource_type=$1
    local resource_id=$2
    
    case $resource_type in
        "artifact_registry_repository")
            gcloud artifacts repositories describe nomadly --location=asia-northeast3 >/dev/null 2>&1
            ;;
        "secret_manager_secret")
            gcloud secrets describe "$resource_id" >/dev/null 2>&1
            ;;
        "workload_identity_pool")
            gcloud iam workload-identity-pools describe github-pool --location=global >/dev/null 2>&1
            ;;
        "workload_identity_pool_provider")
            gcloud iam workload-identity-pools providers describe github-provider --location=global --workload-identity-pool=github-pool >/dev/null 2>&1
            ;;
        "cloud_run_service")
            gcloud run services describe nomadly-api --region=asia-northeast3 >/dev/null 2>&1
            ;;
    esac
}

# Import Artifact Registry if exists
if ! resource_exists "google_artifact_registry_repository.nomadly"; then
    if gcp_resource_exists "artifact_registry_repository" "nomadly"; then
        echo "Importing existing Artifact Registry repository..."
        terraform import google_artifact_registry_repository.nomadly projects/paradox-intern/locations/asia-northeast3/repositories/nomadly || true
    fi
fi

# Import Secrets if exist
if ! resource_exists "google_secret_manager_secret.database_url"; then
    if gcp_resource_exists "secret_manager_secret" "database-url"; then
        echo "Importing existing database URL secret..."
        terraform import google_secret_manager_secret.database_url projects/paradox-intern/secrets/database-url || true
    fi
fi

if ! resource_exists "google_secret_manager_secret.jwt_secret"; then
    if gcp_resource_exists "secret_manager_secret" "jwt-secret"; then
        echo "Importing existing JWT secret..."
        terraform import google_secret_manager_secret.jwt_secret projects/paradox-intern/secrets/jwt-secret || true
    fi
fi

# Import Workload Identity Pool if exists
if ! resource_exists "google_iam_workload_identity_pool.github_pool"; then
    if gcp_resource_exists "workload_identity_pool" "github-pool"; then
        echo "Importing existing Workload Identity Pool..."
        terraform import google_iam_workload_identity_pool.github_pool projects/paradox-intern/locations/global/workloadIdentityPools/github-pool || true
    fi
fi

# Import Workload Identity Pool Provider if exists
if ! resource_exists "google_iam_workload_identity_pool_provider.github_provider"; then
    if gcp_resource_exists "workload_identity_pool_provider" "github-provider"; then
        echo "Importing existing Workload Identity Pool Provider..."
        terraform import google_iam_workload_identity_pool_provider.github_provider projects/paradox-intern/locations/global/workloadIdentityPools/github-pool/providers/github-provider || true
    fi
fi

# Import Cloud Run service if exists
if ! resource_exists "google_cloud_run_v2_service.production"; then
    if gcp_resource_exists "cloud_run_service" "nomadly-api"; then
        echo "Importing existing Cloud Run service..."
        terraform import google_cloud_run_v2_service.production projects/paradox-intern/locations/asia-northeast3/services/nomadly-api || true
    fi
fi

echo "Resource import check completed!"