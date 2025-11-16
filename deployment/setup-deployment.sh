#!/bin/bash

# One-time setup for deployment
# Run this before your first deployment

set -e

PROJECT_ID="nimble-granite-478311-u2"
REGION="europe-west1"

echo "🔧 Setting up deployment environment..."
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if firebase is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

echo "✅ CLI tools found"
echo ""

# Set project
echo "📋 Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

echo "✅ APIs enabled"
echo ""

# Login to Firebase
echo "🔥 Logging into Firebase..."
firebase login

# Initialize Firebase (if not already done)
if [ ! -f "frontend/.firebaserc" ]; then
    echo "📦 Initializing Firebase..."
    cd frontend
    firebase init hosting
    cd ..
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Deploy backend:  ./deploy-backend.sh"
echo "2. Deploy frontend: ./deploy-frontend.sh [backend-url]"
echo ""
echo "See DEPLOYMENT_GUIDE.md for detailed instructions"
