#!/bin/bash

# Deploy Frontend to Firebase Hosting
# Usage: ./deploy-frontend.sh [backend-url]

set -e

BACKEND_URL=$1

if [ -z "$BACKEND_URL" ]; then
  echo "❌ Error: Backend URL required"
  echo "Usage: ./deploy-frontend.sh https://your-backend-url.run.app"
  exit 1
fi

echo "🚀 Deploying Frontend to Firebase Hosting..."

cd frontend

# Update .env with production backend URL
echo "VITE_API_URL=$BACKEND_URL" > .env.production

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Build the app
echo "🔨 Building production bundle..."
npm run build

# Deploy to Firebase
echo "☁️  Deploying to Firebase..."
firebase deploy --only hosting

echo "✅ Frontend deployed successfully!"
echo ""
echo "🌐 Your app is live at:"
firebase hosting:channel:list | grep "live" || echo "Check Firebase Console for URL"
