#!/bin/bash

# Deploy Backend to Google Cloud Run
# Usage: ./deploy-backend.sh

set -e

PROJECT_ID="nimble-granite-478311-u2"
REGION="europe-west1"
SERVICE_NAME="eu-legislation-api"

echo "🚀 Deploying EU Legislation API to Cloud Run..."

# Build and deploy using Cloud Build from project root
gcloud builds submit \
  --config backend/cloudbuild.yaml \
  --project $PROJECT_ID

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your API is now live at:"
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format 'value(status.url)'
