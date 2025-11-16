# Configuration Management Guide

## Overview

The project uses a **centralized configuration system** with support for multiple environments (development, staging, production) and easy CLI overrides. All vector operations, RAG queries, and deployments are now configurable through a single `config.yaml` file.

## Quick Start

### 1. Set Your Environment

```bash
# Use production config (default)
export APP_ENV=production

# Use development config
export APP_ENV=development

# Use staging config
export APP_ENV=staging
```

### 2. Configure `config.yaml`

Edit the main `config.yaml` file in the repository root. Key sections:

- **gcp**: Project ID, bucket, location
- **vector_search**: Index and endpoint configuration
- **rag**: Search and LLM settings
- **environments**: Environment-specific overrides

### 3. Use Scripts with Auto-Config

Scripts automatically load configuration based on `APP_ENV`:

```bash
# Build vector index with config defaults
python scripts/deployment/build_vector_index.py

# Query with config defaults
python scripts/utilities/rag_search.py \
  --index-endpoint <endpoint-name> \
  --query "GDPR data protection"

# Override specific config values
python scripts/deployment/build_vector_index.py \
  --env staging \
  --machine-type e2-standard-8
```

## Configuration Structure

### Vector Search Configuration

```yaml
vector_search:
  index:
    display_name: "eu-legislation-index-production"
    algorithm: "brute_force"  # or "tree_ah"
    dimensions: 768
    distance_measure: "DOT_PRODUCT_DISTANCE"
    shard_size: "SHARD_SIZE_SMALL"
    
  endpoint:
    display_name: "eu-legislation-endpoint-production"
    machine_type: "e2-standard-16"
    min_replicas: 1
    max_replicas: 1
    
  embeddings:
    model: "text-multilingual-embedding-002"
    gcs_prefix: "embeddings_vertexai_json/"
```

### RAG Configuration

```yaml
rag:
  search:
    default_top_k: 50
    use_query_expansion: true
    query_expansion_variants: 2
    
  llm:
    model: "gemini-2.5-pro"
    analysis_chunk_limit: 30
    focus_cross_regulation: true
    
  metadata:
    source: "metadata_store_production.pkl"
    fallback_sources:
      - "processed_chunks"
      - "test_embeddings.jsonl"
    
  risk_categories:
    financial_regulation:
      - "MiFID"
      - "Basel"
      - "banking"
    # ... more categories
```

### Environment Overrides

```yaml
environments:
  development:
    vector_search:
      endpoint:
        machine_type: "e2-standard-2"  # Cheaper for dev
    rag:
      metadata:
        source: "test_embeddings.jsonl"  # Use test data
        
  production:
    vector_search:
      endpoint:
        machine_type: "e2-standard-16"  # Full power for prod
    rag:
      metadata:
        source: "metadata_store_production.pkl"  # Use full data
```

## Using the Config Loader

### In Python Scripts

```python
from config_loader import get_config

# Load config for current environment
config = get_config()

# Access values by dot-path
project_id = config.get('gcp.project_id')
machine_type = config.get('vector_search.endpoint.machine_type')

# Get entire sections
index_config = config.get_index_config()
rag_config = config.get_rag_config()

# Use convenience properties
print(config.project_id)
print(config.embedding_model)
print(config.llm_model)
```

### Environment-Specific Loading

```python
# Explicitly load development config
config = get_config(environment='development')

# Force reload configuration
config = get_config(force_reload=True)
```

## CLI Usage Examples

### Building Vector Index

```bash
# Use default production config
python scripts/deployment/build_vector_index.py

# Use development config
APP_ENV=development python scripts/deployment/build_vector_index.py

# Override specific values
python scripts/deployment/build_vector_index.py \
  --env staging \
  --algorithm tree_ah \
  --machine-type e2-standard-8

# Deploy-only mode
python scripts/deployment/build_vector_index.py \
  --deploy-only projects/123/locations/europe-west1/indexes/456 \
  --machine-type e2-standard-16
```

### RAG Queries

```bash
# Simple query with defaults
python scripts/utilities/rag_search.py \
  --index-endpoint projects/123/.../indexEndpoints/456 \
  --query "GDPR compliance requirements"

# With filters and environment
APP_ENV=production python scripts/utilities/rag_search.py \
  --index-endpoint projects/123/.../indexEndpoints/456 \
  --query "Banking regulation" \
  --risk-category financial_regulation \
  --year-filter 2018

# Filter by language and source type (NEW!)
python scripts/utilities/rag_search.py \
  --index-endpoint projects/123/.../indexEndpoints/456 \
  --query "Finnish banking regulations" \
  --language fi \
  --source-type national_law

# Use paragraph-level context for better LLM analysis (NEW!)
python scripts/utilities/rag_search.py \
  --index-endpoint projects/123/.../indexEndpoints/456 \
  --query "MiFID II capital requirements" \
  --use-paragraphs

# Cross-jurisdictional analysis (NEW!)
python scripts/utilities/rag_search.py \
  --index-endpoint projects/123/.../indexEndpoints/456 \
  --query "Basel III implementation" \
  --source-type international_standard

# Fast mode (no LLM, no expansion)
python scripts/utilities/rag_search.py \
  --index-endpoint projects/123/.../indexEndpoints/456 \
  --query "MiFID II requirements" \
  --no-llm \
  --no-query-expansion

# Override config values
python scripts/utilities/rag_search.py \
  --index-endpoint projects/123/.../indexEndpoints/456 \
  --query "Data protection" \
  --metadata-file custom_metadata.pkl \
  --top-k 100
```

## Configuration Precedence

Configuration values are applied in this order (later takes precedence):

1. **Base config** from `config.yaml`
2. **Environment overrides** (development/staging/production)
3. **Environment variable** (`APP_ENV`)
4. **CLI arguments** (highest precedence)

Example:
```bash
# This uses staging machine_type from config.yaml
APP_ENV=staging python build_vector_index.py

# This overrides with e2-standard-2 regardless of config
APP_ENV=staging python build_vector_index.py --machine-type e2-standard-2
```

## Benefits of This Structure

### ✅ Centralized Configuration
- **Single source of truth** for all settings
- **Easy to maintain** - change once, affects all scripts
- **Version controlled** - track configuration changes

### ✅ Environment Support
- **Development** - Cheaper resources, test data
- **Staging** - Mid-tier resources, production-like setup
- **Production** - Full resources, real data

### ✅ Flexible Overrides
- **CLI arguments** for one-off changes
- **No code modifications** needed
- **Easy experimentation** with different parameters

### ✅ Type Safety & Validation
- **Structured YAML** with clear hierarchy
- **Type hints** in Python code
- **Easy to extend** with new settings

### ✅ Better DX (Developer Experience)
- **Self-documenting** configuration
- **Autocomplete** for config paths
- **Consistent** across all scripts

## Migration from Old Structure

### Before (Hardcoded)
```python
# rag_search.py
PROJECT_ID = "nimble-granite-478311-u2"
LOCATION = "us-central1"
DEPLOYED_INDEX_ID = "eu_legislation_deployed"

# Usage
python rag_search.py --project-id <id> --location <loc> ...
```

### After (Config-Driven)
```yaml
# config.yaml
gcp:
  project_id: "nimble-granite-478311-u2"

rag:
  llm:
    model: "gemini-2.5-pro"
```

```python
# rag_search.py
from config_loader import get_config

config = get_config()
project_id = config.project_id  # Auto-loaded!

# Usage - much simpler!
python rag_search.py --index-endpoint <endpoint> --query "..."
```

## Testing Configuration

Test the configuration loader:

```bash
# Test production config
python scripts/utilities/config_loader.py production

# Test development config
python scripts/utilities/config_loader.py development

# Test staging config
python scripts/utilities/config_loader.py staging
```

Output shows all loaded values:
```
================================================================================
Testing Configuration Loader (environment: production)
================================================================================

✅ Loaded configuration (environment: production)

GCP Configuration:
  Project ID: nimble-granite-478311-u2
  Location: europe-west1
  Bucket: bof-hackathon-data-eu

Vector Search Configuration:
  Index: eu-legislation-index-production
  Algorithm: brute_force
  Dimensions: 768

Endpoint Configuration:
  Endpoint: eu-legislation-endpoint-production
  Machine Type: e2-standard-16
  Replicas: 1-1

RAG Configuration:
  Embedding Model: text-multilingual-embedding-002
  LLM Model: gemini-2.5-pro
  Metadata Source: metadata_store_production.pkl
  Risk Categories: 15 defined

✅ Configuration test complete!
```

## Adding New Configuration

To add new settings:

1. **Update `config.yaml`**:
```yaml
my_new_feature:
  setting1: "value1"
  setting2: 42
```

2. **Add convenience method to `config_loader.py`** (optional):
```python
def get_my_feature_config(self) -> Dict[str, Any]:
    """Get my feature configuration."""
    return self.get_section('my_new_feature')
```

3. **Use in scripts**:
```python
config = get_config()
my_value = config.get('my_new_feature.setting1')
```

## Troubleshooting

### Config file not found
```
FileNotFoundError: Config file not found: config.yaml
```
**Solution**: Run scripts from repository root or set `PYTHONPATH`

### Missing environment section
```
KeyError: 'development' not found in environments
```
**Solution**: Add environment section to `config.yaml` or use `production`

### Import errors
```
ModuleNotFoundError: No module named 'config_loader'
```
**Solution**: Ensure `scripts/utilities` is in Python path or use absolute imports

## Best Practices

1. **Use environments** for different deployment stages
2. **Override with CLI** only for testing/experimentation
3. **Keep secrets out** of config.yaml (use Secret Manager)
4. **Document changes** to config in git commits
5. **Test config changes** in development first
6. **Use defaults** that work for most cases
7. **Validate inputs** in scripts before using config values

## Related Files

- `/config.yaml` - Main configuration file
- `/scripts/utilities/config_loader.py` - Configuration loader
- `/scripts/utilities/metadata_store.py` - Updated to use flexible sources
- `/scripts/deployment/build_vector_index.py` - Uses centralized config
- `/scripts/utilities/rag_search.py` - Uses centralized config
- `/requirements.txt` - Added PyYAML dependency

## Next Steps

1. **Review `config.yaml`** and update values for your project
2. **Set `APP_ENV`** environment variable for your shell
3. **Test scripts** with new configuration system
4. **Add more environments** if needed (e.g., `local`, `testing`)
5. **Extend configuration** for other scripts as needed
