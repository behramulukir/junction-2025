# Deployment Instructions

## Backend Deployment (Cloud Run)

### Option 1: Using Cloud Build (Recommended)
```bash
cd backend
gcloud builds submit --config=cloudbuild.yaml --project=428461461446
```

### Option 2: Manual Docker Build
```bash
# Build from project root
docker build -f backend/Dockerfile -t gcr.io/428461461446/eu-legislation-api .

# Push to Container Registry
docker push gcr.io/428461461446/eu-legislation-api

# Deploy to Cloud Run
gcloud run deploy eu-legislation-api \
  --image gcr.io/428461461446/eu-legislation-api \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars GCP_PROJECT_ID=428461461446,GCP_LOCATION=europe-west1,METADATA_FILE=metadata_store_production.pkl
```

**Backend URL:** https://eu-legislation-api-428461461446.europe-west1.run.app

---

## Frontend Deployment (Firebase Hosting)

### Step 1: Build the frontend
```bash
cd frontend
npm run build
```

### Step 2: Deploy to Firebase
```bash
firebase deploy --only hosting
```

**Frontend URL:** Will be shown after deployment (check Firebase console)

---

## Post-Deployment Checklist

- [ ] Backend deployed successfully
- [ ] Backend health check: `curl https://eu-legislation-api-428461461446.europe-west1.run.app/`
- [ ] Frontend built successfully
- [ ] Frontend deployed to Firebase
- [ ] Frontend connects to backend (check browser console)
- [ ] Test analysis functionality
- [ ] Check that full analysis displays correctly

---

## Quick Deploy Script

Save this as `deploy.sh`:

```bash
#!/bin/bash

echo "🚀 Deploying Backend..."
cd backend
gcloud builds submit --config=cloudbuild.yaml --project=428461461446
cd ..

echo "🎨 Building Frontend..."
cd frontend
npm run build

echo "🔥 Deploying Frontend..."
firebase deploy --only hosting
cd ..

echo "✅ Deployment complete!"
echo "Backend: https://eu-legislation-api-428461461446.europe-west1.run.app"
echo "Check Firebase console for frontend URL"
```

Make it executable: `chmod +x deploy.sh`
Run it: `./deploy.sh`
