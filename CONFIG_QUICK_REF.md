# Configuration Quick Reference

## Environment Setup
```bash
# Set environment (optional, defaults to production)
export APP_ENV=production    # or development, staging
```

## Common Commands

### Build Vector Index
```bash
# Default (uses config.yaml)
python scripts/deployment/build_vector_index.py

# With environment
APP_ENV=development python scripts/deployment/build_vector_index.py

# With overrides
python scripts/deployment/build_vector_index.py \
  --env staging \
  --machine-type e2-standard-8 \
  --algorithm tree_ah
```

### Deploy Existing Index
```bash
python scripts/deployment/build_vector_index.py \
  --deploy-only projects/428461461446/locations/europe-west1/indexes/1609324383250153472 \
  --machine-type e2-standard-16
```

### RAG Query
```bash
# Simple query
python scripts/utilities/rag_search.py \
  --index-endpoint <endpoint-resource-name> \
  --query "Your question here"

# With all filters (NEW: language & source-type)
python scripts/utilities/rag_search.py \
  --index-endpoint <endpoint-resource-name> \
  --query "Banking regulation" \
  --risk-category financial_regulation \
  --year-filter 2018 \
  --language en \
  --source-type eu_legislation \
  --top-k 30

# Finnish national laws (NEW!)
python scripts/utilities/rag_search.py \
  --index-endpoint <endpoint-resource-name> \
  --query "Rahanpesu" \
  --language fi \
  --source-type national_law

# Paragraph-level context (NEW!)
python scripts/utilities/rag_search.py \
  --index-endpoint <endpoint-resource-name> \
  --query "Basel III requirements" \
  --use-paragraphs

# Fast mode (no LLM, no expansion)
python scripts/utilities/rag_search.py \
  --index-endpoint <endpoint-resource-name> \
  --query "Quick search" \
  --no-llm \
  --no-query-expansion
```

## Configuration Hierarchy
```
CLI Arguments (highest priority)
    ↓
Environment Variable (APP_ENV)
    ↓
Environment Config (config.yaml -> environments)
    ↓
Base Config (config.yaml)
```

## Key Config Paths

| Path | Description | Example |
|------|-------------|---------|
| `gcp.project_id` | GCP Project ID | `nimble-granite-478311-u2` |
| `gcp.bucket_name` | GCS Bucket | `bof-hackathon-data-eu` |
| `vector_search.index.algorithm` | Index algorithm | `brute_force` or `tree_ah` |
| `vector_search.endpoint.machine_type` | VM type | `e2-standard-16` |
| `rag.llm.model` | LLM model | `gemini-2.5-pro` |
| `rag.metadata.source` | Metadata file | `metadata_store_production.pkl` |
| `rag.search.default_top_k` | Default results | `50` |

## Python Usage

```python
from config_loader import get_config

# Load config
config = get_config()  # Uses APP_ENV
config = get_config(environment='development')  # Explicit

# Access values
project_id = config.project_id
bucket = config.bucket_name
model = config.llm_model

# Get specific path
value = config.get('vector_search.index.algorithm')
value = config.get('some.path', default='fallback')

# Get section
index_cfg = config.get_index_config()
rag_cfg = config.get_rag_config()
```

## Available Risk Categories

- `data_privacy`
- `financial_regulation`
- `consumer_protection`
- `environmental`
- `health_safety`
- `market_conduct`
- `employment`
- `telecommunications`
- `transport`
- `energy`
- `trade`
- `taxation`
- `insurance`
- `payments`
- `aml_cft`

## Testing

```bash
# Test config loader
python scripts/utilities/config_loader.py production
python scripts/utilities/config_loader.py development

# Test metadata store
python scripts/utilities/metadata_store.py processed_chunks
```

## Common Overrides

```bash
# Development: Use smaller machine, test data
APP_ENV=development python script.py

# Staging: Mid-size machine, full data
APP_ENV=staging python script.py

# Production: Full power
APP_ENV=production python script.py  # or just: python script.py

# Custom one-off: Override anything
python script.py --project-id custom --machine-type e2-standard-2
```

## Files Modified

- ✅ `/config.yaml` - Added vector_search, rag, environments sections
- ✅ `/scripts/utilities/config_loader.py` - New centralized config loader
- ✅ `/scripts/utilities/metadata_store.py` - Support flexible sources
## New Features

✅ **Paragraph Indices Support** - Extract individual paragraphs from chunks
✅ **Multilingual Processing** - Language detection and filtering (EN/FI/multi)
✅ **Source Type Tracking** - EU legislation, national laws, international standards
✅ **Enhanced Metadata** - 17 fields including token_count, regulation_refs, etc.
✅ **Statistics API** - Get language, source type, and chunk type distributions

## Files Modified

- ✅ `/config.yaml` - Added vector_search, rag, environments sections
- ✅ `/scripts/utilities/config_loader.py` - New centralized config loader
- ✅ `/scripts/utilities/metadata_store.py` - Enhanced with paragraph extraction & stats
- ✅ `/scripts/utilities/build_metadata_store.py` - Build from chunks with all fields
- ✅ `/scripts/deployment/build_vector_index.py` - Uses centralized config
- ✅ `/scripts/utilities/rag_search.py` - Uses centralized config
- ✅ `/requirements.txt` - Added pyyaml
- ✅ `/docs/CONFIGURATION_COMPATIBILITY.md` - Compatibility verification report
- ✅ `/scripts/utilities/rag_search.py` - Uses config_loader
- ✅ `/requirements.txt` - Added pyyaml
- ✅ `/docs/CONFIGURATION_GUIDE.md` - Complete guide
