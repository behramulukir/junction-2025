# EU Legislation RAG System - Quick Start Guide

## ✅ System Status

**Vector Search Index:** ✅ Deployed and Ready
- **Endpoint:** `projects/428461461446/locations/europe-west1/indexEndpoints/265576038573015040`
- **Deployed Index ID:** `eu_legislation_deployed`
- **Index:** `projects/428461461446/locations/europe-west1/indexes/3658462213703729152`
- **Embeddings:** 10,000 test samples
- **Metadata:** 264,300 chunks from processed legislation

## 🚀 Quick Search

Run a query:
```bash
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/265576038573015040" \
  --deployed-index-id "eu_legislation_deployed" \
  --query "YOUR QUERY HERE" \
  --top-k 5
```

## 📋 Example Queries

### Data Protection & Privacy
```bash
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/265576038573015040" \
  --deployed-index-id "eu_legislation_deployed" \
  --query "GDPR data protection requirements for financial institutions" \
  --top-k 10
```

### Banking Regulations
```bash
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/265576038573015040" \
  --deployed-index-id "eu_legislation_deployed" \
  --query "capital requirements for banks" \
  --risk-category financial_regulation \
  --top-k 10
```

### Environmental Compliance
```bash
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/265576038573015040" \
  --deployed-index-id "eu_legislation_deployed" \
  --query "emissions trading regulations" \
  --risk-category environmental \
  --top-k 10
```

## 🎯 Risk Categories

Use `--risk-category` to filter results:
- `data_privacy` - GDPR, personal data, data protection
- `financial_regulation` - MiFID, banking, prudential requirements
- `consumer_protection` - Consumer rights, unfair terms
- `environmental` - Emissions, waste management
- `aml_cft` - Money laundering, terrorist financing
- `insurance` - Insurance, reinsurance, Solvency
- `payments` - Payment services, PSD2

## 🔧 Advanced Options

### Disable LLM Analysis
```bash
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/265576038573015040" \
  --deployed-index-id "eu_legislation_deployed" \
  --query "your query" \
  --no-llm
```

### Filter by Year
```bash
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/265576038573015040" \
  --deployed-index-id "eu_legislation_deployed" \
  --query "your query" \
  --year-filter 2020
```

## 🛠️ System Components

### Current Configuration
- **Embedding Model:** `text-embedding-005` (768 dimensions)
- **LLM:** `gemini-2.0-flash-exp`
- **Vector Index:** TreeAH with DOT_PRODUCT distance
- **Metadata Store:** In-memory from processed_chunks (264K entries)

### Files
- `rag_search.py` - Main query interface
- `metadata_store.py` - Metadata loading and storage
- `build_vector_index.py` - Index creation (already done)
- `check_deployment.py` - Check deployment status
- `test_embeddings.jsonl` - 10K test embeddings (59.5 MB)

## 📊 Performance Notes

1. **First Run:** Metadata loading takes ~30 seconds (264K entries)
2. **Subsequent Runs:** Instant (metadata cached in memory)
3. **Query Time:** ~2-5 seconds (includes embedding generation + vector search)
4. **LLM Analysis:** +5-15 seconds (Gemini processing)

## ⚠️ Known Issues

1. **Quota Limits:** Embedding API may hit rate limits
   - System automatically retries with exponential backoff
   - If persistent, wait a few minutes between queries

2. **Metadata Loading:** Initial load is slow
   - Consider pre-caching or using Firestore for production

## 🔄 Future Improvements

1. **Persistent Metadata Store:** Use Firestore/Cloud SQL instead of in-memory
2. **Caching:** Cache query embeddings for common queries
3. **Batch Processing:** Support bulk query processing
4. **Filters:** Implement proper namespace filtering at index level
5. **Full Dataset:** Deploy with all embeddings (not just 10K test samples)

## 📞 Troubleshooting

### Check Deployment Status
```bash
gcloud ai index-endpoints describe 265576038573015040 --region=europe-west1
```

### Monitor with Script
```bash
python check_deployment.py --endpoint-id 265576038573015040
```

### Test Metadata Loading
```bash
python metadata_store.py processed_chunks
```

## 💰 Cost Estimation

**Current Configuration:**
- Index hosting: ~$360/month (n1-standard-16, 2 replicas)
- Embedding API: ~$0.025 per 1K queries
- Gemini API: ~$0.0001875 per 1K input tokens

**Optimizations Available:**
- Switch to e2-standard-2: Save ~$280/month (requires shard size adjustment)
- Cache embeddings: Reduce API costs
- Batch queries: Improve efficiency
