# Deploy EU Legislation API to Google Cloud Run (PowerShell version)

$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_ID = "nimble-granite-478311-u2"
$REGION = "europe-west1"
$SERVICE_NAME = "eu-legislation-api-v2"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deploying EU Legislation API v2" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host ""

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "ERROR: gcloud CLI is not installed" -ForegroundColor Red
    Write-Host "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Set project
Write-Host "Setting project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host ""
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
Write-Host ""
Write-Host "Building and deploying with Cloud Build..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow

# Change to parent directory and submit build
Push-Location ..
try {
    gcloud builds submit --config=junction-2025/cloudbuild.yaml .
} finally {
    Pop-Location
}

# Get service URL
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'
Write-Host ""
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Green
Write-Host "API Docs: $SERVICE_URL/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Test with:" -ForegroundColor Yellow
Write-Host "curl $SERVICE_URL/" -ForegroundColor White
Write-Host ""
