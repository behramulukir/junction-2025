# Deployment Guide - EU Legislation RAG System

## Prerequisites

1. **Google Cloud SDK** installed
   ```bash
   # Install from: https://cloud.google.com/sdk/docs/install
   gcloud --version
   ```

2. **Firebase CLI** installed
   ```bash
   npm install -g firebase-tools
   firebase --version
   ```

3. **Authenticate with Google Cloud**
   ```bash
   gcloud auth login
   gcloud config set project 428461461446
   ```

4. **Enable required APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

## Step 1: Deploy Backend to Cloud Run

```bash
# Make script executable
chmod +x deploy-backend.sh

# Deploy backend
./deploy-backend.sh
```

This will:
- Build a Docker container with your FastAPI app
- Push it to Google Container Registry
- Deploy to Cloud Run in europe-west1
- Output your backend URL (save this!)

**Expected output:**
```
✅ Deployment complete!
🌐 Your API is now live at:
https://eu-legislation-api-xxxxx-ew.a.run.app
```

## Step 2: Deploy Frontend to Firebase

```bash
# Make script executable
chmod +x deploy-frontend.sh

# Deploy frontend (replace with your actual backend URL from Step 1)
./deploy-frontend.sh https://eu-legislation-api-xxxxx-ew.a.run.app
```

This will:
- Update frontend environment variables
- Build production bundle
- Deploy to Firebase Hosting
- Output your frontend URL

## Step 3: Update CORS Settings

After deployment, update your backend CORS to allow your production frontend:

1. Edit `backend/api_server.py`
2. Update the CORS middleware:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:5173",
           "https://your-app.web.app",  # Add your Firebase URL
           "https://your-app.firebaseapp.com"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. Redeploy backend: `./deploy-backend.sh`

## Monitoring & Logs

**Backend logs:**
```bash
gcloud run logs read eu-legislation-api --region europe-west1 --limit 50
```

**View in Cloud Console:**
- Backend: https://console.cloud.google.com/run?project=428461461446
- Frontend: https://console.firebase.google.com/project/428461461446

## Cost Tracking

Monitor your credit usage:
```bash
gcloud billing accounts list
gcloud billing projects describe 428461461446
```

## Troubleshooting

**Backend won't start:**
- Check logs: `gcloud run logs read eu-legislation-api --region europe-west1`
- Verify service account has Vertex AI permissions
- Check metadata_store_production.pkl is included in build

**Frontend can't reach backend:**
- Verify CORS settings include your Firebase domain
- Check backend URL in frontend/.env.production
- Test backend directly: `curl https://your-backend-url.run.app/`

**Out of memory:**
- Increase Cloud Run memory: Add `--memory 4Gi` to cloudbuild.yaml
- Check metadata store size

## Rollback

**Backend:**
```bash
gcloud run services update-traffic eu-legislation-api \
  --to-revisions PREVIOUS_REVISION=100 \
  --region europe-west1
```

**Frontend:**
```bash
firebase hosting:rollback
```

## Security (Optional but Recommended)

Add API key authentication:

1. Generate API key:
   ```bash
   openssl rand -hex 32
   ```

2. Add to backend environment:
   ```bash
   gcloud run services update eu-legislation-api \
     --set-env-vars API_KEY=your-generated-key \
     --region europe-west1
   ```

3. Update frontend to send API key in headers

## Next Steps

- Set up custom domain (Firebase Hosting supports this)
- Enable Cloud Run authentication for sensitive endpoints
- Set up monitoring alerts
- Configure CDN caching for better performance
