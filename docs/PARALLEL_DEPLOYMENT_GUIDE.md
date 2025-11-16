# Parallel Embedding Generation on Google Cloud

## Overview

This guide explains how to run embedding generation across **10 parallel workers** using Google Cloud Run Jobs, reducing processing time from 15-30 minutes to approximately **2-4 minutes**.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Run Job                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐     ┌──────────┐  │
│  │ Worker 0 │ │ Worker 1 │ │ Worker 2 │ ... │ Worker 9 │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘     └────┬─────┘  │
└───────┼───────────┼────────────┼────────────────┼─────────┘
        │           │            │                │
        ▼           ▼            ▼                ▼
   ┌────────────────────────────────────────────────────┐
   │         GCS: processed_chunks/                      │
   │  Worker 0: files 0, 10, 20, 30...                  │
   │  Worker 1: files 1, 11, 21, 31...                  │
   │  Worker 2: files 2, 12, 22, 32...                  │
   │  ...                                                │
   │  Worker 9: files 9, 19, 29, 39...                  │
   └────────────────────────────────────────────────────┘
                         │
                         ▼
   ┌────────────────────────────────────────────────────┐
   │         Vertex AI Text Embeddings API              │
   │     text-multilingual-embedding-002                │
   └────────────────────────────────────────────────────┘
                         │
                         ▼
   ┌────────────────────────────────────────────────────┐
   │         GCS: embeddings_vertexai/                  │
   │  Worker 0 → embeddings_worker00_batch_*.jsonl      │
   │  Worker 1 → embeddings_worker01_batch_*.jsonl      │
   │  ...                                                │
   └────────────────────────────────────────────────────┘
```

## Work Distribution

- **Total files:** 334 batch files
- **Total chunks:** ~334,000 chunks
- **Workers:** 10 parallel instances
- **Per worker:** ~33 files, ~33,400 chunks

### Automatic Sharding

The script uses modulo distribution:
- Worker 0 processes files: 0, 10, 20, 30, ..., 330
- Worker 1 processes files: 1, 11, 21, 31, ..., 331
- Worker 2 processes files: 2, 12, 22, 32, ..., 332
- ...
- Worker 9 processes files: 9, 19, 29, 39, ..., 329

## Deployment Steps

### 1. Quick Deploy (Recommended)

```bash
cd /Users/kavs/Junction/BoF/goldnew/repo
./deploy_parallel_job.sh
```

This script will:
1. Build Docker image with `generate_embeddings_parallel.py`
2. Push image to Google Container Registry
3. Create Cloud Run Job with 10 parallel tasks
4. Execute the job and wait for completion
5. Display logs and output location

### 2. Manual Deployment (Advanced)

#### Step 1: Build and Push Docker Image

```bash
PROJECT_ID="nimble-granite-478311-u2"
IMAGE_NAME="embedding-generator"

gcloud builds submit \
  --project=$PROJECT_ID \
  --tag=gcr.io/$PROJECT_ID/$IMAGE_NAME \
  .
```

#### Step 2: Create Cloud Run Job

```bash
REGION="europe-west1"
JOB_NAME="embedding-generation-parallel"
NUM_WORKERS=10

gcloud run jobs create $JOB_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --image=gcr.io/$PROJECT_ID/$IMAGE_NAME \
  --tasks=$NUM_WORKERS \
  --max-retries=2 \
  --task-timeout=3600 \
  --cpu=2 \
  --memory=4Gi \
  --parallelism=$NUM_WORKERS \
  --args="--project-id=$PROJECT_ID" \
  --args="--location=$REGION" \
  --args="--bucket-name=bof-hackathon-data-eu" \
  --args="--input-prefix=processed_chunks/" \
  --args="--output-prefix=embeddings_vertexai/" \
  --args="--batch-size=100" \
  --args="--write-interval=10000"
```

#### Step 3: Execute the Job

```bash
gcloud run jobs execute $JOB_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --wait
```

## Resource Configuration

| Parameter | Value | Reason |
|-----------|-------|--------|
| **CPU** | 2 vCPU | Adequate for API calls + JSON processing |
| **Memory** | 4 GiB | Handles 10K embedding buffer in memory |
| **Timeout** | 3600s (1 hour) | Safety margin for ~3-5 min workload |
| **Max Retries** | 2 | Handles transient API errors |
| **Parallelism** | 10 | Optimal balance (API limits / speed) |

## Performance Estimates

### Single Worker (Baseline)
- **Chunks:** 334,000
- **Time:** ~15-30 minutes
- **API calls:** ~3,340 (batch_size=100)

### 10 Parallel Workers
- **Chunks per worker:** ~33,400
- **Time per worker:** ~2-4 minutes
- **Total time:** ~2-4 minutes (parallel)
- **Speedup:** **5-10x faster**

### Cost Estimation

**Cloud Run Jobs:**
- CPU: 2 vCPU × 10 workers × 0.07 hours = 1.4 vCPU-hours
- Memory: 4 GiB × 10 workers × 0.07 hours = 2.8 GiB-hours
- **Cost:** ~$0.10-0.20

**Vertex AI Embeddings:**
- Tokens: ~402M tokens
- Rate: $0.025 per 1K tokens
- **Cost:** ~$10.05

**Total:** ~$10.15-10.25

## Monitoring

### View Job Executions

```bash
gcloud run jobs executions list \
  --job=embedding-generation-parallel \
  --region=europe-west1
```

### Stream Logs from All Workers

```bash
# Get latest execution
EXECUTION=$(gcloud run jobs executions list \
  --job=embedding-generation-parallel \
  --region=europe-west1 \
  --limit=1 \
  --format="value(name)")

# View logs
gcloud logging read "resource.type=cloud_run_job \
  AND resource.labels.job_name=embedding-generation-parallel \
  AND resource.labels.location=europe-west1" \
  --limit=100 \
  --format=json
```

### Check Output Files

```bash
# Count generated files
gcloud storage ls gs://bof-hackathon-data-eu/embeddings_vertexai/ | wc -l

# Verify each worker produced output
gcloud storage ls gs://bof-hackathon-data-eu/embeddings_vertexai/ | grep -E "worker[0-9]{2}"
```

Expected output:
```
embeddings_worker00_batch_000000.jsonl
embeddings_worker00_batch_000010.jsonl
...
embeddings_worker09_batch_000009.jsonl
embeddings_worker09_batch_000019.jsonl
```

## Progress Tracking

Each worker displays its own progress bars:
```
================================================================================
🚀 WORKER 1/10 STARTED
================================================================================
  Batch size: 100
  Write interval: 10,000
  Processing 33 files...

📝 Worker 0 chunks |████████████████████| 33,400/33,400 [02:45<00:00, 202.4chunk/s]
🔢 Worker 0 tokens: 40,200,000 tokens

💾 Worker 0: Writing batch 0 (10,000 embeddings)...
  ✓ Worker 0: Uploaded embeddings_worker00_batch_000000.jsonl (10,000 emb, 124 MB)

================================================================================
✅ WORKER 1/10 COMPLETE
================================================================================
Total embeddings generated: 33,400
Total tokens processed: 40,200,000
Estimated cost: $1.01
```

## Troubleshooting

### Job Fails to Start

**Error:** "Service account does not have required permissions"

**Solution:**
```bash
# Grant necessary permissions
PROJECT_ID="nimble-granite-478311-u2"
SERVICE_ACCOUNT=$(gcloud run jobs describe embedding-generation-parallel \
  --region=europe-west1 \
  --format="value(spec.template.spec.serviceAccountName)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"
```

### Workers Timeout

**Error:** Task timeout exceeded (3600s)

**Solution:** Increase timeout or reduce write_interval:
```bash
gcloud run jobs update embedding-generation-parallel \
  --task-timeout=7200 \
  --region=europe-west1
```

### Quota Exceeded Errors

**Error:** "429 Quota exceeded for text embeddings"

**Solution:** Reduce parallelism or batch size:
```bash
# Use 5 workers instead of 10
gcloud run jobs update embedding-generation-parallel \
  --tasks=5 \
  --parallelism=5 \
  --region=europe-west1
```

### Missing Output Files

**Check:** Verify all workers completed successfully:
```bash
gcloud run jobs executions describe EXECUTION_NAME \
  --region=europe-west1 \
  --format="value(status.succeededCount, status.failedCount)"
```

Expected: `10 0` (10 succeeded, 0 failed)

## Cleanup

### Delete the Job

```bash
gcloud run jobs delete embedding-generation-parallel \
  --region=europe-west1 \
  --quiet
```

### Delete Docker Image

```bash
gcloud container images delete gcr.io/nimble-granite-478311-u2/embedding-generator \
  --quiet
```

## Next Steps

After parallel embedding generation completes:

1. **Verify Output**
   ```bash
   gcloud storage ls -l gs://bof-hackathon-data-eu/embeddings_vertexai/
   ```

2. **Build Vector Search Index**
   ```bash
   python scripts/deployment/build_vector_index.py \
     --embeddings-prefix embeddings_vertexai \
     --index-display-name eu-legislation-index \
     --dimensions 768
   ```

3. **Deploy Search Endpoint**
   ```bash
   python scripts/deployment/deploy_quick.py
   ```

## References

- [Cloud Run Jobs Documentation](https://cloud.google.com/run/docs/create-jobs)
- [Vertex AI Text Embeddings API](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [Cloud Run Job Pricing](https://cloud.google.com/run/pricing)
