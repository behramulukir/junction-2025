# Deployment Guide - EU Legislation API v2

This guide explains how to deploy the new backend to Google Cloud Run.

## Prerequisites

1. **Google Cloud SDK** installed and configured
   ```bash
   gcloud --version
   ```

2. **Authenticated with GCP**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

3. **Project set correctly**
   ```bash
   gcloud config set project nimble-granite-478311-u2
   ```

## Quick Deploy

### Windows (PowerShell)
```powershell
cd junction-2025
.\deploy.ps1
```

### Linux/Mac (Bash)
```bash
cd junction-2025
chmod +x deploy.sh
./deploy.sh
```

## Manual Deployment

If you prefer to deploy manually:

```bash
# 1. Set project
gcloud config set project nimble-granite-478311-u2

# 2. Enable APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 3. Build and deploy (from project root)
cd ..
gcloud builds submit --config=junction-2025/cloudbuild.yaml .

# 4. Get service URL
gcloud run services describe eu-legislation-api-v2 \
  --region=europe-west1 \
  --format='value(status.url)'
```

## What Gets Deployed

The deployment includes:
- FastAPI API server (`api_server.py`)
- SQLite caching layer (`cache_db.py`)
- RAG search system (`scripts/utilities/rag_search.py`)
- Metadata store (`metadata_store_all.pkl` - 149,927 entries)
- Configuration (`config.yaml`)

## Cloud Run Configuration

- **Service Name**: `eu-legislation-api-v2`
- **Region**: `europe-west1`
- **Memory**: 4 GiB
- **CPU**: 2
- **Max Instances**: 10
- **Timeout**: 300 seconds
- **Authentication**: Public (unauthenticated access allowed)

## After Deployment

1. **Get the service URL**:
   ```bash
   gcloud run services describe eu-legislation-api-v2 \
     --region=europe-west1 \
     --format='value(status.url)'
   ```

2. **Test the API**:
   ```bash
   curl https://YOUR-SERVICE-URL/
   ```

3. **View API documentation**:
   ```
   https://YOUR-SERVICE-URL/docs
   ```

4. **Update frontend** to use the new URL:
   - Edit `frontend/.env`
   - Set `VITE_API_URL=https://YOUR-SERVICE-URL`

## Replacing Old Backend

To replace the old backend deployment:

1. **Deploy the new backend** (as above)
2. **Test the new backend** thoroughly
3. **Update frontend** to point to new URL
4. **Delete old service** (optional):
   ```bash
   gcloud run services delete eu-legislation-api \
     --region=europe-west1
   ```

## Monitoring

View logs:
```bash
gcloud run services logs read eu-legislation-api-v2 \
  --region=europe-west1 \
  --limit=50
```

View service details:
```bash
gcloud run services describe eu-legislation-api-v2 \
  --region=europe-west1
```

## Troubleshooting

### Build fails with "metadata_store_all.pkl not found"
Make sure you've run the metadata build command first:
```bash
python scripts/utilities/build_metadata_store.py \
  --from-chunks gs://bof-hackathon-data-eu/processed_chunks \
  --output metadata_store_all.pkl
```

### Service crashes on startup
Check logs:
```bash
gcloud run services logs read eu-legislation-api-v2 \
  --region=europe-west1 \
  --limit=100
```

### Out of memory errors
Increase memory in `cloudbuild.yaml`:
```yaml
- '--memory'
- '8Gi'  # Increase from 4Gi
```

## Cost Optimization

- Service scales to zero when not in use
- First 2 million requests per month are free
- Caching reduces LLM API calls significantly
- Consider setting `--max-instances` lower if needed

## Security Notes

- Service is currently public (unauthenticated)
- To add authentication, remove `--allow-unauthenticated` from cloudbuild.yaml
- Consider adding API key authentication in production
- Metadata store contains public EU legislation data
